<?php
namespace DataExport\Exporters\CBExport;

trait BusinessFAQTrait
{
    public function getBusinessFAQImportID( int $businessID, string $question ): string
    {
        return "scraper-bbb--bfaq:{$businessID}-".md5( strtolower( trim( $question ) ) );
    }

    public function isBusinessFAQExists( int $businessID, string $importID, ?string $question )
    {
        $checker = $this->inputChecker;

        $checker->empty( $businessID, "Param: businessID is empty" );
        $checker->empty( $importID, "Param: importID is empty" );

        if ( $question !== null )
        {
            $checker->empty( $question, "Param: 'question' is empty" );
        }

        if ( $checker->has() )
        {
            return false;
        }

        $row = $this->db->selectRow( "id", "bname_faq_imports", [ "import_id" => $importID ] );
        $this->throwExceptionIf( $row === false, $this->db->getExtendedError() );

        if ( $row )
        {
            return (int)$row[ "id" ];
        }

        if ( $question !== null )
        {
            $row = $this->db->selectRow(
                "ID",
                "bname_faq",
                "bname_id = '{$businessID}' and lower(question) = '". $this->db->escape( strtolower( trim( $question ) ) )."'"
            );
            $this->throwExceptionIf( $row === false, $this->db->getExtendedError() );
            if ( $row )
            {
                return (int)$row[ "ID" ];
            }
        }

        return 0;
    }

    public function removeBusinessFAQByImportID( string $importID )
    {
        return $this->removeRecordByImportID( "bname_faq", $importID );
    }

    public function addBusinessFAQ( string $importID, array $fields )
    {
        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $checker->empty( $fields["question"], "Field: 'question' is empty" );
        $checker->empty( $fields["answer"], "Field: 'answer' is empty" );
        $checker->empty( $fields["business_id"], "Field: 'business_id' is empty" );
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $faqID = $this->isBusinessFAQExists( $fields["business_id"], $importID, $fields["question"] );
        if ( $faqID > 0 ) return $faqID;

        $rs = $this->db->insert( "bname_faq", [
            "bname_id" => $fields["business_id"],
            "question" => $fields["question"],
            "answer" => $fields["answer"],
            "status" => "published",
            "create_date" => date( "Y-m-d H:i:s" ),
        ] );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "bname_faq", $id, $importID, $fields["import_data"] );

        return $id;
    }
}