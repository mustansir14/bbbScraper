<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;

final class CommentTest extends TestCase
{
    private function getExport()
    {
        global $db;

        $cb = new CBExport( $db );

        return $cb;
    }

    public function testGetImportId(): void
    {
        $export = $this->getExport();

        $value = $export->getCommentImportID( __FUNCTION__ );

        $this->assertNotEmpty( $value, "Import id empty" );
    }

    private function addCompany( string $name )
    {
        $export = $this->getExport();

        $importId = $export->getCompanyImportID( $name );

        {
            $companyId = $export->addCompany( $importId, [
                "name"        => $name,
                "import_data" => $name,
            ] );
            $this->assertIsInt( $companyId, "Result not int" );
            $this->assertTrue( $companyId > 0, "Company id zero" );
        }

        {
            $exists = $export->isCompanyExists( $importId, $name );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists > 0, "Company exists, but must not exists" );
        }

        return $companyId;
    }

    private function addComplaint( int $companyId )
    {
        $export = $this->getExport();

        $importId = $export->getComplaintImportID( __FUNCTION__ );

        {
            $complaintId = $export->addComplaint( $importId, [
                "company_id"  => $companyId,
                "subject"     => __FUNCTION__,
                "text"        => __FUNCTION__,
                "date"        => date( "Y-m-d" ),
                "user_name"   => __FUNCTION__,
                "import_data" => __FUNCTION__,
            ] );
            $this->assertIsInt( $complaintId, "Result not int" );
            $this->assertTrue( $complaintId > 0, "Company id zero" );
        }

        {
            $exists = $export->isComplaintExists( $importId );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists > 0, "Company exists, but must not exists" );
        }

        return $complaintId;
    }

    public function testInsertComment(): void
    {
        $export = $this->getExport();

        $companyId = $this->addCompany( __FUNCTION__ );
        $complaintId = $this->addComplaint( $companyId );
        $importId  = $export->getCommentImportID( __FUNCTION__ );

        {
            $exists = $export->isCommentExists( $importId );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Complaint exists, but must not exists" );
        }

        {
            $id = $export->addComment( $importId, [
                "complaint_id"  => $complaintId,
                "text"        => "text",
                "date"        => date( "Y-m-d" ),
                "user_name"   => __FUNCTION__,
                "import_data" => __FUNCTION__,
                "is_update"   => false,
            ] );
            $this->assertIsInt( $id, "Result not int: ".$export->getErrorsAsString() );
            $this->assertTrue( $id > 0, "Comment id zero" );
        }

        {
            $exists = $export->isCommentExists( $importId );
            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists == $id, "Comment exists, but must not exists" );
        }

        $this->assertTrue( $export->removeCommentByImportID( $importId ), "Can not remove comment" );

        {
            $exists = $export->isCommentExists( $importId );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Comment exists, but must not exists" );
        }
    }
}
