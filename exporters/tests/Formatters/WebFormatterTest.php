<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Formatters\WebFormatter;

final class WebFormatterTest extends TestCase
{
    public function provideWebs(): array
    {
        return [
            [ "fonts.google.com", "https://fonts.google.com" ],
            [ "complaints.co.za", "https://www.complaints.co.za" ],
            [ "www.one.lv", "https://www.one.lv" ],
            [ "one.lv", "https://www.one.lv" ],
            # trash
            [ "http://www.butcherbox.com/", "https://www.butcherbox.com/" ],
            [ "http://www.yellowpages.com/cambridge-ma/mip/butcherbox-528595097", "" ],
            [ "https://www.manta.com/c/mhxhby9/butcherbox-llc", "" ],
            [ "Additional Business Informatio", "" ],
            [ "ADDITIONAL INFO", "" ],
            [ "More information, including Brands Sold, Products Sold, Month in Operation, Provides Delivery, Pet Friendly and more.", "" ],
        ];
    }

    /**
     * @dataProvider provideWebs
     */
    public function testWebs( $web, $mustBe )
    {
        $this->assertSame( WebFormatter::format( $web ), $mustBe );
    }
}
