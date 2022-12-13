<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;
use DataExport\Helpers\Db;

final class CityTest extends TestCase
{
    static string $countryName = __CLASS__."Country";
    static string $countryCode = "CT1";
    static int $countryID = 0;

    static string $stateName = __CLASS__."State";
    static string $stateCode = "CT2";
    static int $stateID = 0;

    static string $cityName = __CLASS__."City";
    static string $cityCode = "CT3";
    static int $cityID = 0;

    private function getExport()
    {
        global $db;

        $cb = new CBExport( $db, "" );

        return $cb;
    }

    public static function tearDownAfterClass(): void
    {
        global $db;

        $db->delete( 'cities', [ 'city_name' => self::$cityName ] ) or die( $db->getExtendedError() );
        $db->delete( 'states', [ 'state_name' => self::$stateName ] ) or die( $db->getExtendedError() );
        $db->delete( 'countries', [ 'country_name' => self::$countryName ] ) or die( $db->getExtendedError() );
    }

    public static function setUpBeforeClass(): void
    {
        global $db;

        self::tearDownAfterClass();

        $db->insert( "countries", [
            "address" => self::$countryName,
            "country_name" => self::$countryName,
            "country_code" => self::$countryCode,
        ] );

        self::$countryID = $db->insertID();
        if ( (int)self::$countryID < 1 ) throw new \Exception( $db->getExtendedError() );

        $db->insert( "states", [
            "countries_id" => self::$countryID,
            "address" => self::$stateName,
            "state_name" => self::$stateName,
            "state_code" => self::$stateCode,
        ]);

        self::$stateID = $db->insertID();
        if ( (int)self::$stateID < 1 ) throw new \Exception( $db->getExtendedError() );

        $db->insert( "cities", [
            "country_id" => self::$countryID,
            "states_id"  => self::$stateID,
            "address" => self::$cityName,
            "city_name" => self::$cityName,
        ]);

        self::$cityID = $db->insertID();
        if ( (int)self::$cityID < 1 ) throw new \Exception( $db->getExtendedError() );
    }

    public function testCityExists()
    {
        $this->assertIsInt( self::$countryID );
        $this->assertIsInt( self::$stateID );
        $this->assertIsInt( self::$cityID );

        $export = $this->getExport();

        $this->assertFalse( $export->isCityExists( 0, 0, self::$cityName ) );
        $this->assertFalse( $export->isCityExists( self::$countryID, 0, self::$cityName ) );
        $this->assertFalse( $export->isCityExists( 0, self::$stateID, self::$cityName ) );

        $this->assertSame( $export->isCityExists( self::$countryID, self::$stateID, self::$cityName ), self::$cityID );

        $this->assertSame( $export->isCityExists( self::$countryID + 1, self::$stateID, self::$cityName ), 0 );
        $this->assertSame( $export->isCityExists( self::$countryID, self::$stateID + 1, self::$cityName ), 0 );
        $this->assertSame( $export->isCityExists( self::$countryID, self::$stateID + 1, self::$cityName."111" ), 0 );
    }

    public function testCityAdd()
    {
        $this->assertIsInt( self::$countryID );
        $this->assertIsInt( self::$stateID );

        $export = $this->getExport();

        $cityName = __FUNCTION__;
        $importID = $export->getCityImportID( self::$countryID, self::$stateID, $cityName );

        $cityID = $export->addCity( $importID, [
            "country" => self::$countryName,
            "state" => self::$stateName,
            "name" => $cityName,
            "import_data" => __FUNCTION__,
        ]);
        $this->assertIsInt( $cityID, $export->getErrorsAsString() );
        $this->assertTrue( $cityID > 0, $export->getErrorsAsString() );

        $this->assertSame( $export->isCityExists( self::$countryID, self::$stateID, $cityName ), $cityID );

        $export->removeCityByImportID( $importID );
        $this->assertSame( $export->isCityExists( self::$countryID, self::$stateID, $cityName ), 0 );
    }
}
