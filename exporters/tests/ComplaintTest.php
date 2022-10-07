<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;

final class ComplaintTest extends TestCase
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

        $value = $export->getComplaintImportID( __FUNCTION__ );

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

    public function testInsertComplaint(): void
    {
        $export = $this->getExport();

        $companyId = $this->addCompany( __FUNCTION__ );
        $importId  = $export->getComplaintImportID( __FUNCTION__ );

        {
            $exists = $export->isComplaintExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Complaint exists, but must not exists" );
        }

        {
            $id = $export->addComplaint( $importId, [
                "company_id"  => $companyId,
                "subject"     => "subject",
                "text"        => "text",
                "date"        => date( "Y-m-d" ),
                "user_name"   => __FUNCTION__,
                "import_data" => __FUNCTION__,
            ] );
            $this->assertIsInt( $id, "Result not int" );
            $this->assertTrue( $id > 0, "Company id zero" );
        }

        {
            $exists = $export->isComplaintExists( $importId, __FUNCTION__ );
            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists == $id, "Company exists, but must not exists" );
        }

        $this->assertTrue( $export->removeComplaintByImportID( $importId ), "Can not remove company" );

        {
            $exists = $export->isComplaintExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Company exists, but must not exists" );
        }
    }
}
