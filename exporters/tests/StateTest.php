<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;
use DataExport\Helpers\Db;

final class StateTest extends TestCase
{
    static string $countryName = __CLASS__."Country";
    static string $countryCode = "ST1";
    static int $countryID = 0;

    static string $stateName = __CLASS__."State";
    static string $stateCode = "ST2";
    static int $stateID = 0;

    private function getExport()
    {
        global $db;

        $cb = new CBExport( $db, "" );

        return $cb;
    }

    public static function tearDownAfterClass(): void
    {
        global $db;

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
    }

    public function testStateExists()
    {
        $this->assertIsInt( self::$countryID );
        $this->assertIsInt( self::$stateID );

        $export = $this->getExport();

        $this->assertSame( $export->isStateExists( 0, self::$stateName ), 0 );
        $this->assertSame( $export->isStateExists( 1, self::$stateName ), 0 );

        global $db;

        $firstCountryID = (int)$db->selectColumn( "country_id", "cities", "country_id<>".self::$countryID, false, "states_id", 1 );
        $this->assertIsInt( $firstCountryID );
        $this->assertTrue( $firstCountryID > 0 );
        $this->assertNotSame( $firstCountryID, self::$countryID );

        $this->assertSame( $export->isStateExists( $firstCountryID, self::$stateName ), 0 );
        $this->assertSame( $export->isStateExists( self::$countryID, self::$stateName ), self::$stateID );
    }

    public function testStateExistShort()
    {
        $this->assertIsInt( self::$countryID );
        $this->assertIsInt( self::$stateID );

        $export = $this->getExport();

        $this->assertSame( $export->isStateExistsByShortName( 0, self::$stateCode ), false );
        $this->assertSame( $export->isStateExistsByShortName( 1, self::$stateCode ), 0 );
        $this->assertSame( $export->isStateExistsByShortName(  self::$countryID, self::$stateName ), 0 );
        $this->assertSame( $export->isStateExistsByShortName( self::$countryID, self::$stateCode ), self::$stateID );
    }

    public function testStateExistFull()
    {
        $this->assertIsInt( self::$countryID );
        $this->assertIsInt( self::$stateID );

        $export = $this->getExport();

        $this->assertSame( $export->isStateExistsByFullName( 0, self::$stateName ), false );
        $this->assertSame( $export->isStateExistsByFullName( 1, self::$stateName ), 0 );
        $this->assertSame( $export->isStateExistsByFullName(  self::$countryID, self::$stateName ), self::$stateID );
        $this->assertSame( $export->isStateExistsByFullName( self::$countryID, self::$stateCode ), 0 );
    }
}
