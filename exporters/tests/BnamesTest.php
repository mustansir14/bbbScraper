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

    public function testProfileStatus()
    {
        $export = $this->getExport();

        $names = [ __FUNCTION__."-11", __FUNCTION__."-22" ];
        $imports = [ $export->getBusinessImportID( $names[0] ), $export->getBusinessImportID( $names[1] ) ];

        $this->assertTrue( $export->isBusinessExists( $imports[0], $names[0] ) === 0 );
        $this->assertTrue( $export->isBusinessExists( $imports[1], $names[1] ) === 0 );

        $this->assertTrue( $export->addBusiness( $imports[0], [
            "name"        => $names[0],
            "import_data" => $names[0],
        ] ) > 0 );

        $this->assertTrue( $export->addBusiness( $imports[1], [
                "name"        => $names[1],
                "import_data" => $names[1],
            ] ) > 0 );

        $this->assertTrue( $export->isBusinessExists( $imports[0], $names[0] ) !== 0 );
        $this->assertTrue( $export->isBusinessExists( $imports[1], $names[1] ) !== 0 );

        {
            $export->enableBusiness( $imports[ 0 ] );
            $export->disableBusiness( $imports[ 1 ] );

            $this->assertTrue( $export->isBusinessActive( $imports[ 0 ] ) );
            $this->assertFalse( $export->isBusinessActive( $imports[ 1 ] ) );
        }

        {
            $export->disableBusiness( $imports[ 0 ] );
            $export->enableBusiness( $imports[ 1 ] );

            $this->assertFalse( $export->isBusinessActive( $imports[ 0 ] ) );
            $this->assertTrue( $export->isBusinessActive( $imports[ 1 ] ) );
        }

        $export->removeBusinessByImportID( $imports[0] );
        $export->removeBusinessByImportID( $imports[1] );
    }
}
