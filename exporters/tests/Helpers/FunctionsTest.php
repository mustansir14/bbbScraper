<?php
declare(strict_types = 1);

use PHPUnit\Framework\TestCase;
use DataExport\Helpers\Functions;

final class FunctionsTest extends TestCase
{
    public function testTextLines()
    {
        $lines = Functions::getTextLines("some complaintsboard.com text...   in space!!!");
        $this->assertSame($lines, [
            "some complaintsboard.com text...   ",
            "in space!!!"
        ]);


        $lines = Functions::getTextLines("some complaintsboard.com text $7.203, in space! New sentense");
        $this->assertSame($lines, [
            "some complaintsboard.com text $7.203, in space! ",
            "New sentense"
        ]);
    }

    private function removeTimePart($datetime)
    {
        return explode(" ", $datetime)[ 0 ];
    }

    public function testDateOlderThenOneYear()
    {
        $dateOlderOneYear = date("Y-m-d", time() - 365 * 24 * 3600);
        $this->assertSame(
            $this->removeTimePart(Functions::getPostDate($dateOlderOneYear)),
            date("Y-m-d", time() - 365 * 24 * 3600)
        );
        $dateOlderOneYear = date("Y-m-d", time() - 712 * 24 * 3600);
        $this->assertSame(
            $this->removeTimePart(Functions::getPostDate($dateOlderOneYear)),
            date("Y-m-d", time() - 365 * 24 * 3600)
        );
    }

    public function testDateInYear()
    {
        foreach (range(1, 10000) as $nbr) {
            $dateInOneYear = date("Y-m-d", time() - 180 * 24 * 3600);
            $dateReturned = Functions::getPostDate($dateInOneYear);
            $dateReturnedTime = strtotime($dateReturned);
            #echo $dateReturned."\n";
            #echo "time: ".date( "Y-m-d H:i:s", time())."\n";
            #echo "retr: ".date( "Y-m-d H:i:s", $dateReturnedTime)."\n";
            #var_dump($dateReturnedTime >= time() - 90 * 24 * 3600,$dateReturnedTime <= time());
            $this->assertTrue(
                $dateReturnedTime >= time() - 90 * 24 * 3600 && $dateReturnedTime <= time(),
                "Try date: {$dateInOneYear}, returned: {$dateReturned}"
            );
        }
    }

    public function testCommentDate()
    {
        foreach (range(1, 10000) as $nbr) {
            $dateReturned = Functions::getCommentDate();
            $dateReturnedTime = strtotime($dateReturned);
            #echo $dateReturned."\n";
            #var_dump($dateReturnedTime >= time() - 90 * 24 * 3600,$dateReturnedTime <= time());
            $this->assertTrue(
                $dateReturnedTime >= strtotime(date("Y-m-d", time() - 7 * 24 * 3600)) && $dateReturnedTime <= time(),
                "Returned: {$dateReturned}"
            );
        }
    }

}