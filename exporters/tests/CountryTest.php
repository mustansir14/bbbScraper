<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;
use DataExport\Helpers\Db;

final class CountryTest extends TestCase
{
    static int $countryID = 0;
    static string $countryName = "TestCountryName";
    static string $coutryCode = "CN1";

    private function getExport()
    {
        global $db;

        $cb = new CBExport( $db, "" );

        return $cb;
    }

    public static function tearDownAfterClass(): void
    {
        global $db;

        $db->delete( 'countries', [ 'country_name' => self::$countryName ] ) or die( $db->getExtendedError() );
    }

    public static function setUpBeforeClass(): void
    {
        global $db;

        self::tearDownAfterClass();

        $db->insert( "countries", [
            "address" => "aaaaaaa",
            "country_name" => static::$countryName,
            "country_code" => static::$coutryCode,
        ] );
        static::$countryID = $db->insertID();
        if ( (int)self::$countryID < 1 ) throw new \Exception( $db->getExtendedError() );
    }

    public function testCountryExistsByFullName(): void
    {
        global $db;

        $export = $this->getExport();

        $this->assertIsInt( static::$countryID );

        {
            $exists = $export->isCountryExistsByFullName( static::$countryName."-invalid-name" );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, 0 );
        }

        {
            $exists = $export->isCountryExistsByFullName( static::$countryName );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, static::$countryID );
        }

        {
            $name = static::$countryName;
            $name[2] = strtoupper( $name[2] );
            $exists = $export->isCountryExistsByFullName( $name );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, static::$countryID );
        }

        {
            $exists = $export->isCountryExistsByFullName( "a" );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, 0 );
        }
    }

    public function testCountryExistsByShortName(): void
    {
        global $db;

        $export = $this->getExport();

        $this->assertIsInt( static::$countryID );

        {
            $exists = $export->isCountryExistsByShortName( "aaaa" );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, 0 );
        }

        {
            $exists = $export->isCountryExistsByShortName( static::$coutryCode );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, static::$countryID );
        }

        {
            $mixName = static::$coutryCode;
            $mixName[0] = strtoupper( $mixName[0] );
            $exists = $export->isCountryExistsByShortName( $mixName );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, static::$countryID );
        }

        {
            $exists = $export->isCountryExistsByShortName( "a" );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, 0 );
        }

        {
            $exists = $export->isCountryExistsByShortName( "DAC" );

            $this->assertIsInt( $exists );
            $this->assertSame( $exists, 0 );
        }
    }
}
