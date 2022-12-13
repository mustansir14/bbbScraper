<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;

final class CompanyTest extends TestCase
{
    private function getExport()
    {
        global $db;

        $cb = new CBExport( $db, "" );

        return $cb;
    }

    public function testGetImportId(): void
    {
        $export = $this->getExport();

        $value = $export->getCompanyImportID( __FUNCTION__ );

        $this->assertNotEmpty( $value, "Import id empty" );
    }

    public function testInsertCompany(): void
    {
        $export = $this->getExport();

        $importId = $export->getCompanyImportID( __FUNCTION__ );

        {
            $exists = $export->isCompanyExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Company exists, but must not exists" );
        }

        {
            $companyId = $export->addCompany( $importId, [
                "name"        => __FUNCTION__,
                "import_data" => __FUNCTION__,
            ] );
            $this->assertIsInt( $companyId, "Result not int" );
            $this->assertTrue( $companyId > 0, "Company id zero" );
        }

        {
            $exists = $export->isCompanyExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists > 0, "Company exists, but must not exists" );
        }

        $this->assertTrue( $export->removeCompanyByImportID( $importId ), "Can not remove company" );

        {
            $exists = $export->isCompanyExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Company exists, but must not exists" );
        }
    }
}
