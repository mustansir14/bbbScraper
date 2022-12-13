<?php
namespace DataExport\Exporters;

use DataExport\Exporters\ExportInterface;
use DataExport\Exporters\ErrorsAsStringInterface;
use DataExport\Helpers\InputChecker;
use DataExport\Helpers\Db;
use DataExport\Exporters\CBExport\CountryTrait;
use DataExport\Exporters\CBExport\StateTrait;
use DataExport\Exporters\CBExport\CityTrait;
use DataExport\Exporters\CBExport\CategoryTrait;
use DataExport\Exporters\CBExport\BusinessFAQTrait;
use GuzzleHttp\Client;
use GuzzleHttp\Psr7\Utils;

class CBExport implements ExportInterface, ErrorsAsStringInterface
{
    use CountryTrait, StateTrait, CityTrait, CategoryTrait, BusinessFAQTrait;

    private Db $db;
    private InputChecker $inputChecker;
    private string $apiHost;

    public function __construct( Db $db, ?string $apiHost )
    {
        $this->db = $db;
        $this->inputChecker =  new InputChecker( $db );
        $this->apiHost = $apiHost;
    }

    public function getErrors(): array
    {
        return $this->inputChecker->get();
    }

    public function getErrorsAsString(): string
    {
        return implode( "\n", $this->getErrors() );
    }

    private function throwException( string $text )
    {
        throw new \Exception( $text );
    }

    private function throwExceptionIf( bool $condition, string $text )
    {
        if ( $condition )
        {
            $this->throwException( $text );
        }
    }

    private function removeRecordByImportID( string $table, string $importID )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $rs = $this->db->delete( $table, "id = ( select id from {$table}_imports where import_id = '".$this->db->escape( $importID )."')" );
        if ( $rs ) return true;

        $checker->append( $this->db->getExtendedError() );

        return false;
    }

    private function isRecordExists( string $table, string $importID, ?string $name, ?string $nameField = null )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );

        if ( $nameField )
        {
            $checker->empty( $name, "Param: name is empty" );
        }

        if ( $checker->has() )
        {
            return false;
        }

        $row = $this->db->selectRow( "id", $table."_imports", [ "import_id" => $importID ] );
        $this->throwExceptionIf( $row === false, $this->db->getExtendedError() );

        if ( $row )
        {
            return (int)$row[ "id" ];
        }

        if ( $nameField && $name )
        {
            $row = $this->db->selectRow( "ID", $table, [ $nameField => trim( $name ) ] );
            $this->throwExceptionIf( $row === false, $this->db->getExtendedError() );
            if ( $row )
            {
                return (int)$row[ "ID" ];
            }
        }

        return 0;
    }

    private function getImport( string $table, int $id ): ?array
    {
        $importData = $this->db->selectRow( '*', $table.'_imports', [ 'id' => $id ] );
        $this->throwExceptionIf( $importData === false , $this->db->getError() );

        return $importData;
    }

    public function addImport( $table, $id, $importID, $importData ):void
    {
        $rs = $this->db->insert( $table. "_imports", [
            "id" => $id,
            "import_id" => $importID,
            "import_data" => json_encode( $importData ),
            "import_create" => [ "NOW()" ],
            "import_update" => [ "NOW()" ],
        ]);
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );
    }

    #####################################################################################################

    public function getCompanyImportID( $companyId ): string
    {
        return "scraper-bbb--company-id:{$companyId}";
    }

    public function removeCompanyByImportID( string $importID ): bool
    {
        $checker = $this->inputChecker;

        # Fix: Can't update table 'compl_companies' in stored function/trigger because it is already used by statement which invoked this stored function/trigger

        $companyID = $this->db->selectColumn( "id", "compl_companies_imports", [ "import_id" => $importID ] );
        if ( !$companyID )
        {
            return true;
        }

        # delete all comments
        $complaints = $this->db->selectArray( "ID", "compl_complaints", [ "compl_company" => $companyID ] );
        if ( $complaints === false )
        {
            $checker->append( $this->db->getExtendedError() );
            return false;
        }

        foreach( $complaints as $complaint )
        {
            $rs = $this->db->delete( "compl_posts", [ "compl_id" => $complaint["ID"] ] );
            if ( !$rs )
            {
                $checker->append( $this->db->getExtendedError() );
                return false;
            }

            // BugFix: delete by one because too long delete many in one request
            $rs = $this->db->delete( "compl_complaints", [ "id" => $complaint["ID"] ] );
            if ( !$rs )
            {
                $checker->append( $this->db->getExtendedError() );
                return false;
            }
        }

        return $this->removeRecordByImportID( "compl_companies", $importID );
    }

    public function isCompanyExists( string $importID, string $name ): int
    {
        return $this->isRecordExists( "compl_companies", $importID, $name, "company_name" );
    }

    public function addCompany( string $importID, array $fields )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $checker->empty( $fields["name"], "Field: 'name' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $companyID = $this->isCompanyExists( $importID, $fields["name"] );
        if ( $companyID > 0 ) return $companyID;

        $rs = $this->db->insert( "compl_companies", [
            "company_name" => $fields["name"],
        ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "compl_companies", $id, $importID, $fields["import_data"] );

        return $id;
    }

    public function hasBusiness( int $companyID ): int
    {
        $businessID = $this->db->selectColumn( "bname_id", "compl_companies", [ "ID" => $companyID ] );
        $this->throwExceptionIf( $businessID === false, $this->db->getExtendedError() );

        $bnameRow = $this->db->selectRow( 'id', 'bnames', 'id = "'.$businessID.'"');
        if ( !$bnameRow ) return 0;

        return $businessID > 0 ? $businessID : 0;
    }

    #####################################################################################################

    public function getBusinessImportID( $companyId ): string
    {
        return "scraper-bbb--company-id:{$companyId}";
    }

    public function updateBusiness( string $importID, array $fields ): bool
    {
        $businessID = $this->isBusinessExists( $importID, null );
        if ( !$businessID ) return false;

        $rs = $this->db->update( "bnames", $fields, [ "ID" => $businessID ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        return true;
    }

    public function isBusinessExported( string $importID, string $name ): bool
    {
        if( !$this->isBusinessExists( $importID, $name ) )
        {
            return false;
        }

        return $this->isBusinessExists( $importID, null );
    }

    public function disableBusiness( string $importID ): bool
    {
        return $this->updateBusiness( $importID, [
            "bname_profile_status" => 0,
        ]);
    }

    public function enableBusiness( string $importID ): bool
    {
        return $this->updateBusiness( $importID, [
            "bname_profile_status" => 1,
        ]);
    }

    public function getBusiness( string $importID ): ?array
    {
        $businessID = $this->isBusinessExists( $importID, null );
        if ( !$businessID ) return null;

        $row = $this->db->selectRow( "*", "bnames", [ "ID" => $businessID ] );
        $this->throwExceptionIf( $row === false, $this->db->getExtendedError() );

        return $row;
    }

    public function removeBusinessByImportID( string $importID )
    {
        return $this->removeRecordByImportID( "bnames", $importID );
    }

    private function encodeAsDubleArray( $values )
    {
        $values = is_array( $values ) ? $values : [ $values ];
        $values = array_map( function ( $value ) {
            return [ $value ];
        }, $values );

        # need set format [["239-549-2628"],["+1 (239) 542-4395",""]]

        return json_encode( $values );
    }

    public function setBusinessLogo( string $importID, string $imageContent ): bool
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $imageContent, "Param: imageContent is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $businessID = $this->isBusinessExists( $importID, null );
        if ( !$businessID )
        {
            $checker->append( 'Can not find business id' );

            return false;
        }

        try
        {
            $client = new Client( [
                'base_uri' => $this->apiHost,
                'verify'  => false,
                'timeout' => 20,
                #'debug' => true,
                #'proxy' => 'http://localhost:8888',
            ] );

            $response = $client->post( "/api/business/logo?id={$businessID}&token=jdf89jo343kgjs8gfds895jk3g", [
                'multipart' => [
                    [
                        'name'     => 'image',
                        'contents' => $imageContent,
                        'filename' => 'image.png',
                    ]
                ]
            ]);

            if ( $response->getStatusCode() != 200 ) return $this->setError( "Http code not 200" );

            $json = json_decode($response->getBody()->getContents());
            if ( !$json ) {
                $checker->append( $response->getBody()->getContents()."\nJson decode fail");
                return false;
            }
            if ( !$json->success ) {
                $checker->append( implode( "\n", $json->errors ) );
                return false;
            }

            return true;
        }catch (\Exception $e ) {
            $checker->append( $e->getMessage() );
        }

        return false;
    }

    public function addBusiness( string $importID, array $fields )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $checker->empty( $fields["name"], "Field: 'name' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $businessID = $this->isBusinessExists( $importID, $fields["name"] );
        if ( $businessID > 0 ) return $businessID;

        $insertFields = [
            "bname_name" => $fields["name"],
            "bname_profile_status" => 1,
        ];

        if ( isset( $fields["address"] ) )
        {
            if ( !$checker->empty( $fields["country"], "Field: 'country' is empty" ) )
            {
                $countryID = $this->isCountryExists( $fields['country'] );
                if ( !$countryID )
                {
                    $checker->append( 'Can not find country' );
                }

                $fields["country"] = $countryID;
            }

            if ( !$checker->empty( $fields["state"], "Field: 'state' is empty" ) && $countryID )
            {
                $stateID = $this->isStateExists( $countryID, $fields['state'] );
                if ( !$stateID )
                {
                    $checker->append( 'Can not find state' );
                }

                $fields["state"] = $stateID;
            }

            $checker->empty( $fields["city"], "Field: 'city' is empty" );
            $checker->empty( $fields["address"], "Field: 'address' is empty" );
            $checker->empty( $fields["zip"], "Field: 'zip' is empty" );

            if ( $checker->has() )
            {
                return false;
            }

            $insertFields["bname_country"] = $fields["country"];
            $insertFields["bname_state"] = $fields["state"];
            $insertFields["bname_city"] = $fields["city"];
            $insertFields["bname_address"] = $fields["address"];
            $insertFields["bname_zip"] = $fields["zip"];
        }

        if ( isset( $fields["ltd"] ) )
        {
            $insertFields["bname_ltd"] = $fields["ltd"];
        }

        if ( isset( $fields["phone"] ) && $fields["phone"] )
        {
            $insertFields["bname_phone"] = $this->encodeAsDubleArray( $fields["phone"] );
        }

        if ( isset( $fields["fax"] ) && $fields["fax"] )
        {
            $insertFields["bname_fax"] = $this->encodeAsDubleArray( $fields["fax"] );
        }

        if ( isset( $fields["website"] ) && $fields["website"] )
        {
            $insertFields["bname_website"] = $this->encodeAsDubleArray( $fields["website"] );
        }

        if ( isset( $fields["category"] ) )
        {
            $categoryID = $this->isCategoryExists( $fields["category"] );
            if ( $categoryID )
            {
                $insertFields["bname_category_id"] = $categoryID;
            } else {
                $checker->append( "Category not exists" );
                return false;
            }
        }

        if ( isset( $fields["hours"] ) )
        {
            $insertFields["bname_hours"] = $fields["hours"];
        }

        $rs = $this->db->insert( "bnames", $insertFields );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "bnames", $id, $importID, $fields["import_data"] );

        return $id;

    }

    public function linkCompanyToBusiness( int $companyId, int $businessId ): bool
    {
        $checker = $this->inputChecker;

        $checker->empty( $companyId, "Param: companyId is empty" );
        $checker->empty( $businessId, "Param: businessId is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $checker->dbRowNotExists( "bnames", $businessId, "Business not exists" );
        $checker->dbRowNotExists( "compl_companies", $companyId, "Company not exists" );

        if ( $checker->has() )
        {
            return false;
        }

        $companyRow = $this->db->selectRow( "id, bname_id", "compl_companies", [ "id" => $companyId ] );
        if ( !$companyRow ) {
            $checker->append( "Company with id: {$companyId} not exists" );
            return false;
        }

        $rs = $this->db->update( "compl_companies", [
            "bname_id" => $businessId,
        ], [ "id" => $companyId ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        return true;
    }

    public function isBusinessActive( string $importID ): bool
    {
        $businessID = $this->isBusinessExists( $importID, null );
        if ( !$businessID ) return false;

        $status = $this->db->selectColumn( "bname_profile_status", "bnames", [ "ID" => $businessID ] );
        $this->throwExceptionIf( $status === false, $this->db->getExtendedError() );

        return (bool)$status;
    }

    public function isBusinessExists( string $importID, ?string $name )
    {
        return $this->isRecordExists( "bnames", $importID, $name, ( $name === null ? null : "bname_name" ) );
    }

    #####################################################################################################

    public function getComplaintImportID( $complaintId ): string
    {
        return "scraper-bbb--complaint-id:{$complaintId}";
    }

    public function getComplaintImportIDLike(): string
    {
        return $this->getComplaintImportID( '%' );
    }

    public function getAllImportedComplaints( int $businessID ): array
    {
        $rows = $this->db->selectArray(
            "cc.*, ci.*",
            [ "compl_complaints cc", "compl_complaints_imports ci" => "ci.id = cc.id" ],
            "cc.compl_bname_id = '{$businessID}' and ci.import_id like '".$this->getComplaintImportIDLike()."'"
        );
        $this->throwExceptionIf( $rows === false, $this->db->getError() );

        return $rows;
    }

    public function removeComplaintByImportID( string $importID )
    {
        $complaintID = $this->isComplaintExists( $importID );
        if ( $complaintID )
        {
            $complaintRow = $this->db->selectRow( 'ID, uid', 'compl_complaints', [ 'id' => $complaintID ] );
            $this->throwExceptionIf( !$complaintRow, $this->db->getExtendedError() );

            $importData = $this->getImport( "panel_users", $complaintRow[ 'uid' ] );
            if ( $importData )
            {
                $this->throwExceptionIf( !$this->removeUserByImportID( $importData[ 'import_id' ] ), $this->getErrorsAsString() );
            }
        }

        return $this->removeRecordByImportID( "compl_complaints", $importID );
    }

    public function spamComplaint( string $importID, string $reason )
    {
        $complaintID = $this->isComplaintExists( $importID );
        if ( $complaintID ) {
            $this->db->update( "compl_complaints", [
                'is_spam' => 2,
                'spam_reason' => $reason,
            ], "ID = '{$complaintID}'" );
        }
    }

    public function unspamComplaint( string $importID )
    {
        $complaintID = $this->isComplaintExists( $importID );
        if ( $complaintID ) {
            $this->db->update( "compl_complaints", [
                'is_spam' => 0,
                'spam_reason' => null,
            ], "ID = '{$complaintID}'" );
        }
    }

    public function addComplaint( string $importID, array $fields )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        if ( !$checker->empty( $fields["company_id"], "Field: 'company_id' is empty" ) )
        {
            $checker->dbRowNotExists( "compl_companies", $fields["company_id"], "Company not exists" );
        }
        $checker->empty( $fields["subject"], "Field: 'subject' is empty" );
        $checker->empty( $fields["text"], "Field: 'text' is empty" );
        $checker->empty( $fields["date"], "Field: 'date' is empty" );
        $checker->empty( $fields["user_name"], "Field: 'user_name' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );
        $checker->empty( $fields["type"], "Field: 'type' is empty, must be complaint or review" );

        if ( $checker->has() )
        {
            return false;
        }

        $complaintID = $this->isComplaintExists( $importID );
        if ( $complaintID > 0 ) return $complaintID;

        $insertFields = [
            "compl_type" => $fields["type"] === "review" ? "review" : "complaint",
            "compl_company" => $fields["company_id"],
            "compl_subject" => $fields["subject"],
            "compl_text" => $fields["text"],
            "compl_time" => $fields["date"],
            "compl_country" => 3,
        ];

        if ( isset( $fields["isOpen"] ) && $fields["isOpen"] )
        {
            $insertFields["compl_lock"] = 1;
        }

        if ( isset( $fields["is_resolved"] ) && $fields["is_resolved"] )
        {
            $insertFields["isResolved"] = 1;

            $checker->empty( $fields["resolved_date"], "Field: 'resolved_date' is empty" );

            if ( $checker->has() )
            {
                return false;
            }

            $insertFields["resolvedTime"] = $fields["resolved_date"];
        }

        $userID = $this->addUser( $this->getUserImportID( $fields["user_name"] ), $fields );
        if ( !$userID ) return false;

        $insertFields["uid"] = $userID;

        $rs = $this->db->insert( "compl_complaints", $insertFields );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "compl_complaints", $id, $importID, $fields["import_data"] );

        return $id;
    }

    public function isComplaintExists( string $importID )
    {
        return $this->isRecordExists( "compl_complaints", $importID, "", null );
    }

    ######################################################################################

    public function getUserImportID( $userId ): string
    {
        return "scraper-bbb--user-name-md5:".md5( $userId );
    }

    public function removeUserByImportID( string $importID )
    {
        return $this->removeRecordByImportID( "panel_users", $importID );
    }

    public function isUserExists( string $importID, ?string $userName )
    {
        return $this->isRecordExists( "panel_users", $importID, $userName, ( $userName ? "displayname" : null ) );
    }

    public function addUser( string $importID, array $fields )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $checker->empty( $fields["user_name"], "Field: 'user_name' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $userID = $this->isUserExists( $importID, $fields["user_name"] );
        if ( $userID > 0 ) return $userID;

        $insertFields = [
            "displayname" => $fields["user_name"],
            "email" => $fields["user_email"] ?? "bbb.mustansir.".md5( microtime() )."@cbexport.php",
            "email_confirm" => 1,
            "password" => md5( __CLASS__ ),
            "added" => $fields["user_date"] ?? [ "NOW()" ],
        ];

        if ( isset( $fields["user_support"] ) )
        {
            $checker->dbRowNotExists( "bnames", $fields["user_support"], "Can not find BN for support user" );
            if ( $checker->has() )
            {
                return false;
            }

            $insertFields["bnameID"] = $fields["user_support"];
        }

        $rs = $this->db->insert( "panel_users", $insertFields );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "panel_users", $id, $importID, $fields["import_data"] );

        return $id;
    }

    ######################################################################################

    public function getCommentImportID( $commentId ): string
    {
        return "scraper-bbb--complaint-id:".$commentId;
    }

    public function getAllImportedComments( int $businessID )
    {
        $rows = $this->db->selectArray(
            "cp.*, ci.*",
            [ "compl_posts cp", "compl_posts_imports ci" => "ci.id = cp.id", "compl_complaints cc" => "cc.id = cp.compl_id" ],
            "cc.compl_bname_id = '{$businessID}' and ci.import_id like '".$this->getComplaintImportIDLike()."'"
        );
        $this->throwExceptionIf( $rows === false, $this->db->getError() );

        return $rows;
    }

    public function isCommentExists( string $importID )
    {
        return $this->isRecordExists( "compl_posts", $importID, "", null );
    }

    public function removeCommentByImportID( string $importID )
    {
        $commentID = $this->isCommentExists( $importID );
        if ( $commentID )
        {
            $commentRow = $this->db->selectRow( 'ID, uid', 'compl_posts', [ 'id' => $commentID ] );
            $this->throwExceptionIf( !$commentRow, $this->db->getExtendedError() );

            $importData = $this->getImport( "panel_users", $commentRow[ 'uid' ] );
            if ( $importData )
            {
                $this->throwExceptionIf( !$this->removeUserByImportID( $importData[ 'import_id' ] ), $this->getErrorsAsString() );
            }
        }

        return $this->removeRecordByImportID( "compl_posts", $importID );
    }

    public function addComment( string $importID, array $fields )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        if ( !$checker->empty( $fields["complaint_id"], "Field: 'complaint_id' is empty" ) )
        {
            $checker->dbRowNotExists( "compl_complaints", $fields["complaint_id"], "Complaint not exists" );
        }

        $checker->empty( $fields["text"], "Field: 'text' is empty" );
        $checker->empty( $fields["date"], "Field: 'date' is empty" );
        $checker->notBool( $fields["is_update"], "Field: 'is_update' is empty" );
        $checker->empty( $fields["user_name"], "Field: 'user_name' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $userID = $this->addUser( $this->getUserImportID( $fields["user_name"] ), $fields );
        if ( !$userID ) return false;

        $id = $this->isCommentExists( $importID );
        if ( $id > 0 ) return $id;

        $rs = $this->db->insert( "compl_posts", [
            "compl_id" => $fields["complaint_id"],
            "post_text" => $fields["text"],
            "post_time" => $fields["date"],
            "is_updated" => $fields["is_update"] ? 1 : 0,
            "uid" => $userID,
        ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "compl_posts", $id, $importID, $fields["import_data"] );

        return $id;
    }

    ############################################################################################

    public function callUpdateComplaint( int $complaintID )
    {
        $rs = $this->db->query( "CALL updateComplaint({$complaintID})" );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );
    }

    public function callUpdateCompany( int $companyID )
    {
        $rs = $this->db->query( "CALL updateCompany({$companyID})" );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );
    }

    public function callUpdateBusiness( int $businessID )
    {
        $rs = $this->db->query( "CALL updateBname({$businessID})" );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );
    }
}