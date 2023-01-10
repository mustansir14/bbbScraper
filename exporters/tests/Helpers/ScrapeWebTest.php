<?php
declare(strict_types = 1);

use PHPUnit\Framework\TestCase;
use DataExport\Helpers\ScrapeWeb;

final class ScrapeWebTest extends TestCase
{
    public function testTextLines()
    {
        $scraper = new ScrapeWeb();
        $return = $scraper->getSocials("https://www.dealdash.com/");

        $this->assertIsArray($return);

        $this->assertCount(1, $return["linkedin_url"] ?? [] );
        $this->assertEquals("https://www.linkedin.com/company/dealdash",$return["linkedin_url"][0]);

        $this->assertCount(1, $return["facebook_url"] ?? [] );
        $this->assertEquals("https://www.facebook.com/DealDash",$return["facebook_url"][0]);

        $this->assertCount(1, $return["twitter_url"] ?? [] );
        $this->assertEquals("https://twitter.com/DealDash",$return["twitter_url"][0]);

        $this->assertCount(1, $return["youtube_url"] ?? [] );
        $this->assertEquals("https://www.youtube.com/DealDashOfficial",$return["youtube_url"][0]);

        $this->assertCount(1, $return["instagram_url"] ?? [] );
        $this->assertEquals("https://www.instagram.com/dealdashofficial",$return["instagram_url"][0]);

        $this->assertCount(1, $return["pinterest_url"] ?? [] );
        $this->assertEquals("https://www.pinterest.com/dealdash/",$return["pinterest_url"][0]);
    }

}