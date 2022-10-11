<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;

final class BnamesTest extends TestCase
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

        $value = $export->getBusinessImportID( __FUNCTION__ );

        $this->assertNotEmpty( $value, "Import id empty" );
    }

    public function testInsertBusiness(): void
    {
        $export = $this->getExport();

        $importId = $export->getBusinessImportID( __FUNCTION__ );

        {
            $exists = $export->isBusinessExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Business exists '".__FUNCTION__."', but must not exists" );
        }

        {
            $companyId = $export->addBusiness( $importId, [
                "name"        => __FUNCTION__,
                "import_data" => __FUNCTION__,
            ] );
            $this->assertIsInt( $companyId, "Result not int" );
            $this->assertTrue( $companyId > 0, "Business id zero" );
        }

        {
            $exists = $export->isBusinessExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists > 0, "Business exists, but must not exists" );
        }

        $this->assertTrue( $export->removeBusinessByImportID( $importId ), "Can not remove Business" );

        {
            $exists = $export->isBusinessExists( $importId, __FUNCTION__ );

            $this->assertIsInt( $exists, "Result not int" );
            $this->assertTrue( $exists === 0, "Business exists, but must not exists" );
        }
    }
}
