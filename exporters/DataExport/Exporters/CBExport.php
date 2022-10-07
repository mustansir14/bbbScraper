<?php
namespace DataExport\Exporters;

use DataExport\Exporters\ExportInterface;
use DataExport\Exporters\ErrorsAsStringInterface;
use DataExport\Helpers\InputChecker;
use DataExport\Helpers\Db;

class CBExport implements ExportInterface, ErrorsAsStringInterface
{
    private Db $db;
    private InputChecker $inputChecker;

    public function __construct( Db $db )
    {
        $this->db = $db;
        $this->inputChecker =  new InputChecker();
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

    private function isRecordExists( string $table, string $importID, string $name, ?string $nameField = null )
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

        if ( $nameField )
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

        return $businessID > 0 ? $businessID : 0;
    }

    #####################################################################################################

    public function getBusinessImportID( $companyId ): string
    {
        return "scraper-bbb--company-id:{$companyId}";
    }

    public function removeBusinessByImportID( string $importID )
    {
        return $this->removeRecordByImportID( "bnames", $importID );
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

        $rs = $this->db->insert( "bnames", [
            "bname_name" => $fields["name"],
        ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "compl_companies", $id, $importID, $fields["import_data"] );

        return $id;

    }

    public function isBusinessExists( string $importID, string $name )
    {
        return $this->isRecordExists( "bnames", $importID, $name, "bname_name" );
    }

    #####################################################################################################

    public function getComplaintImportID( $complaintId ): string
    {
        return "scraper-bbb--complaint-id:{$complaintId}";
    }

    public function removeComplaintByImportID( string $importID )
    {
        return $this->removeRecordByImportID( "compl_complaints", $importID );
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

        $checker->empty( $fields["company_id"], "Field: 'company_id' is empty" );
        $checker->empty( $fields["subject"], "Field: 'subject' is empty" );
        $checker->empty( $fields["text"], "Field: 'text' is empty" );
        $checker->empty( $fields["date"], "Field: 'date' is empty" );
        $checker->empty( $fields["user_name"], "Field: 'user_name' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $userID = $this->addUser( $this->getUserImportID( $fields["user_name"] ), $fields );
        if ( !$userID ) return false;

        $complaintID = $this->isComplaintExists( $importID );
        if ( $complaintID > 0 ) return $complaintID;

        $rs = $this->db->insert( "compl_complaints", [
            "compl_company" => $fields["company_id"],
            "compl_subject" => $fields["subject"],
            "compl_text" => $fields["text"],
            "compl_time" => $fields["date"],
            "uid" => $userID,
        ] );
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

        $rs = $this->db->insert( "panel_users", [
            "displayname" => $fields["user_name"],
            "email" => "noreply.".md5( microtime() )."@cbexport.php",
            "email_confirm" => 1,
            "password" => md5( __CLASS__ ),
            "added" => [ "NOW()" ],
        ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "panel_users", $id, $importID, $fields["import_data"] );

        return $id;
    }

}