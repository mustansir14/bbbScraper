<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Formatters\HoursFormatter;

final class HoursFormatterTest extends TestCase
{
    public function createDays( $monday, $tuesday, $wednesday, $thurday, $friday, $saturday, $sunday )
    {
        return [
            "monday" => $monday,
            "tuesday"
        ];
    }

    public function getFormatTypes(): array
    {
        return [
            [
              <<<TXT
Sales Hours
Mon-Fri: 8am to 11pm EST / 5am to 8pm PST
Sat: 8am to 10pm EST / 5am to 7pm PST
Sun: Closed

Service Hours
Mon-Fri: 8am to 5pm EST / 5am to 2pm PST
Sat-Sun: Closed
TXT
              ,
null
            ],
            [
              <<<TXT
Primary
M:
Open 24 Hours
T:
Open 24 Hours
W:
Open 24 Hours
Th:
Open 24 Hours
F:
Open 24 Hours
TXT
              ,
              [
                  "monday" => [ "type" => "open24" ],
                  "tuesday" => [ "type" => "open24" ],
                  "wednesday" => [ "type" => "open24" ],
                  "thursday" => [ "type" => "open24" ],
                  "friday" => [ "type" => "open24" ],
                  "saturday" => [ "type" => "closed" ],
                  "sunday" => [ "type" => "closed" ],
              ]

            ],
            [
              <<<TXT
Primary
Su:
Closed
TXT
              ,
              null
            ],
            [
                <<<TXT
Primary
T:
10:30 AM - 5:30 PM
W:
10:30 AM - 5:30 PM
Th:
10:30 AM - 5:30 PM
F:
10:30 AM - 5:30 PM
Sa:
10:00 AM - 4:00 PM
TXT,
                [
                    "monday" => [ "type" => "closed" ],
                    "tuesday" => [ "type" => "range", "from" => "10:30", "to" => "17:30" ],
                    "wednesday" => [ "type" => "range", "from" => "10:30", "to" => "17:30" ],
                    "thursday" => [ "type" => "range", "from" => "10:30", "to" => "17:30" ],
                    "friday" => [ "type" => "range", "from" => "10:30", "to" => "17:30" ],
                    "saturday" => [ "type" => "range", "from" => "10:00", "to" => "16:00" ],
                    "sunday" => [ "type" => "closed" ],
                ]
            ]
        ];
    }
    /**
     * @dataProvider getFormatTypes
     */
    public function testFormatTypes( string $text, ?array $mustBe ): void
    {
        $this->assertSame( HoursFormatter::fromString( $text ), $mustBe );
    }
}
