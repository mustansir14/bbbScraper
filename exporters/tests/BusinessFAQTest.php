<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;
use DataExport\Helpers\Db;

final class BusinessFAQTest extends TestCase
{
    private static $businessName = __CLASS__."Business";
    private static $businessID = 0;

    private function getExport()
    {
        global $db;

        $cb = new CBExport( $db );

        return $cb;
    }

    public static function tearDownAfterClass(): void
    {
        global $db;

        $db->delete( 'bnames', [ 'bname_name' => self::$businessName ] ) or die( $db->getExtendedError() );
    }

    public static function setUpBeforeClass(): void
    {
        global $db;

        self::tearDownAfterClass();

        $db->insert( "bnames", [
            "bname_name" => static::$businessName,
            "bname_profile_status" => 1,
        ] );
        static::$businessID = $db->insertID();
        if ( (int)self::$businessID < 1 ) throw new \Exception( $db->getExtendedError() );
    }

    public function testFAQ(): void
    {
        $this->assertIsInt( static::$businessID );

        $export = $this->getExport();

        $question = __FUNCTION__;
        $importID = $export->getBusinessFAQImportID( static::$businessID, $question );

        $this->assertSame( $export->isBusinessFAQExists( static::$businessID, $importID, null ), 0 );
        $this->assertSame( $export->isBusinessFAQExists( static::$businessID, $importID, $question ), 0 );

        $faqID = $export->addBusinessFAQ( $importID, [
           "business_id" => static::$businessID,
           "question" => $question,
           "answer" => __FUNCTION__,
           "import_data" => __FUNCTION__,
        ]);

        $this->assertIsInt( $faqID );
        $this->assertTrue( $faqID > 0 );
        $this->assertSame( $export->isBusinessFAQExists( static::$businessID, $importID, null ), $faqID );
        $this->assertSame( $export->isBusinessFAQExists( static::$businessID, $importID, $question ), $faqID );

        $faqID2 = $export->addBusinessFAQ( $importID, [
            "business_id" => static::$businessID,
            "question" => $question,
            "answer" => __FUNCTION__,
            "import_data" => __FUNCTION__,
        ]);

        $this->assertSame( $faqID, $faqID2 );

        $this->assertTrue( $export->removeBusinessFAQByImportID( $importID ) );

        $this->assertSame( $export->isBusinessFAQExists( static::$businessID, $importID, null ), 0 );
        $this->assertSame( $export->isBusinessFAQExists( static::$businessID, $importID, $question ), 0 );
    }
}
