<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Helpers\Functions;

final class FunctionsTest extends TestCase
{
    public function testDateOlderThenOneYear()
    {
        $dateOlderOneYear = date( "Y-m-d",time() - 365 * 24 * 3600);
        $this->assertSame( Functions::getPostDate( $dateOlderOneYear ), date("Y-m-d", time() - 365 * 24 * 3600) );

        $dateOlderOneYear = date( "Y-m-d",time() - 712 * 24 * 3600);
        $this->assertSame( Functions::getPostDate( $dateOlderOneYear ), date("Y-m-d", time() - 365 * 24 * 3600) );
    }

    public function testDateInYear()
    {
        foreach( range( 1, 10000 ) as $nbr )
        {
            $dateInOneYear = date( "Y-m-d", time() - 180 * 24 * 3600 );
            $dateReturned = Functions::getPostDate( $dateInOneYear );
            $dateReturnedTime = strtotime( $dateReturned );

            #echo $dateReturned."\n";
            #var_dump($dateReturnedTime >= time() - 90 * 24 * 3600,$dateReturnedTime <= time());

            $this->assertTrue(
                $dateReturnedTime >= time() - 90 * 24 * 3600 && $dateReturnedTime <= time(),
                "Try date: {$dateInOneYear}, returned: {$dateReturned}" );
        }
    }
}