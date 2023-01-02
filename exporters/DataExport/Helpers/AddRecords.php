<?php

namespace DataExport\Helpers;

use DataExport\Formatters\TextFormatter;
use DataExport\Helpers\Functions;
use DataExport\Helpers\GoogleTextChecker;

class AddRecords
{
    private array $vars;
    private $faker;

    public function __construct($vars)
    {
        $this->vars = $vars;
        $this->faker = \Faker\Factory::create();

        foreach( ['companyNameWithoutAbbr','exporter','isInsert','destCompanyID','destBusinessID','sourceCompanyRow','importInfoScraper','makeSpamComplaints','counter','checkTextInGoogle'] as $name ) {
            if ( !array_key_exists( $name, $this->vars )
                || ( is_string( $this->vars[$name] ) && empty( $this->vars[$name]) )
                || ( is_int( $this->vars[$name] ) && $this->vars[$name] < 1 )
                || ( is_array( $this->vars[$name] ) && count( $this->vars) == 0 )
                || is_null( $this->vars[$name] )
            ) {
                debug_print_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS);
                die( "Error: key {$name} not exists in vars" );
            }
        }

        $this->counter = $this->vars['counter'];
    }

    private function getTextLines(string $text)
    {
        $parts = preg_split( '#([\.\!\?]{1,}(?!com|net|info|org)\s*)#si', $text, -1 , PREG_SPLIT_DELIM_CAPTURE);
        $lines = [];

        for($i = 0; $i < count( $parts ); $i += 2 )
        {
            $lines[] = $parts[$i].($parts[$i+1] ?? "");
        }

        return $lines;
    }
    
    private function addComplaint( object $exporter, array $row, string $type )
    {
        $complaintText = TextFormatter::fixText( $row["{$type}_text"], 'complaintsboard.com' );
        if ( $complaintText )
        {
            echo ($this->counter++).") ".$row["{$type}_id"].") ".$row[ "{$type}_date" ].": ".substr( $complaintText, 0, 60 )."...\n";

            if( $this->vars['checkTextInGoogle'] )
            {
                echo "Checking in google...\n";
                $checker = new GoogleTextChecker();
                $response = $checker->test( $complaintText );
                if ( !$response )
                {
                    die( "Google text checker error: ".$checker->getError() );
                }
                echo "Google matched: ".( (string)$response->data )."\n".$response->url."\n";
                if ( $response->data > 0 )
                {
                    echo "EXIST IN GOOGLE, skip\n";

                    return 0;
                }
            }

            $subject = "";
            foreach ( $this->getTextLines($row[ "{$type}_text" ]) as $line )
            {
                $subject .= $line;
                if ( mb_strlen( $subject, "utf-8" ) >= 40 )
                {
                    break;
                }
            }
            $subject = trim( $subject );
            $subject = mb_substr( $subject, 0, 145, "utf-8" );
            $subject = stripos( $subject, ' ' ) !== false ? preg_replace( "#[a-z0-9']{1,}$#si", "", $subject ) : $subject;
            $subject = trim( $subject, ".," );
            #echo "Insert complaint\n";
            #print_r( $complaint );

            $resolvedDate = false;
            $makeResolved = $this->vars['ifResponseMakeResolved'] ?? false;

            if ( $makeResolved ) {
                $updateText = TextFormatter::fixText( $row["company_response_text"], 'complaintsboard.com' );
                if ( $updateText ) {
                    $resolvedDate = $row[ "company_response_date" ];
                }
            }

            $useDate = Functions::getPostDate( $row[ "{$type}_date" ] );

            $fakeUserName = substr( $this->faker->firstName(), 0, 1 ).". ".$this->faker->lastName();
            $complaintID = $exporter->addComplaint( $exporter->getComplaintImportID( $row[ "{$type}_id" ], $type ), [
                "company_id"  => $this->vars['destCompanyID'],
                "subject"     => $subject,
                "text"        => $complaintText,
                "type"        => $type,
                "date"        => $useDate,
                "stars"       => $row["{$type}_rating"] ?? 0,
                "user_name"   => $fakeUserName,
                "user_date"   => date( "Y-m-d", strtotime( $useDate ) - 60 ),
                "is_resolved"  => $resolvedDate ?: 0,
                "resolved_date" => $resolvedDate ?: null,
                "isOpen"      => 1,
                "import_data" => [
                    "company_id"   => $this->vars['sourceCompanyRow'][ "company_id" ],
                    "{$type}_id" => $row[ "{$type}_id" ],
                    "company_url"  => $this->vars['sourceCompanyRow'][ "url" ],
                    "type"         => $type,
                    "scraper"      => $this->vars['importInfoScraper'],
                    "version"      => 1,
                ],
            ] );
            if ( !$complaintID )
            {
                die( $exporter->getErrorsAsString() );
            }

            if ( $this->vars['makeSpamComplaints'] )
            {
                $exporter->spamComplaint(
                    $exporter->getComplaintImportID( $row[ "{$type}_id" ], $type ),
                    basename( __FILE__ ).": make private"
                );
            }
            else
            {
                $exporter->unspamComplaint( $exporter->getComplaintImportID( $row[ "{$type}_id" ] ) );
            }

            return $complaintID;
        }

        return 0;
    }

    private function addResponse( object $exporter, array $row, int $complaintID, string $type )
    {
        if ( $row["company_response_text"] )
        {
            $userName = "{$this->vars['companyNameWithoutAbbr']} Support";

            $updateText = TextFormatter::fixText( $row["company_response_text"], 'complaintsboard.com' );
            if ( $updateText )
            {
                echo "Update: ".substr( $updateText, 0, 60 )."\n";

                $commentID = $exporter->addComment( $exporter->getCommentImportID( $row[ "{$type}_id" ], $type ), [
                    "complaint_id" => $complaintID,
                    "text"         => $updateText,
                    "is_update"    => true,
                    "date"         => $row[ "company_response_date" ],
                    "user_name"    => $userName,
                    "user_date"    => date( "Y-m-d", strtotime( $row[ "company_response_date" ] ) - 1 * 365 * 24 * 3600 ),
                    "user_email"   => $this->faker->email(),
                    "user_support" => $this->vars['destBusinessID'],
                    "import_data"  => [
                        "company_id"   => $this->vars['sourceCompanyRow'][ "company_id" ],
                        "{$type}_id"   => $row[ "{$type}_id" ],
                        "company_url"  => $this->vars['sourceCompanyRow'][ "url" ],
                        "type"         => "{$type}-response",
                        "scraper"      => $this->vars['importInfoScraper'],
                        "version"      => 1,
                    ],
                ] );
                if ( !$commentID )
                {
                    die( $exporter->getErrorsAsString() );
                }
            }
        }
    }

    private function insertComplaintOrReview( array $item, string $type ): int
    {
        $exporter = $this->vars['exporter'];

        if ( $this->vars['isInsert'] ) {
            $complaintID = $this->addComplaint( $exporter, $item, $type );
            if ( $complaintID )
            {
                $this->addResponse( $exporter, $item, $complaintID, $type );

                $exporter->callUpdateComplaint( $complaintID );
            }

            return $complaintID;
        }

        return 0;
    }

    public function insertReview( array $review ): int
    {
        return $this->insertComplaintOrReview( $review, "review" );
    }

    public function insertComplaint( array $complaint ): int
    {
        return $this->insertComplaintOrReview( $complaint, "complaint" );
    }

    public function insertAsComment( array $complaint, int $toComplaintID, string $type )
    {
        $exporter = $this->vars['exporter'];

        if ( $this->vars['isInsert'] ) {
            $updateText = TextFormatter::fixText( $complaint["{$type}_text"], 'complaintsboard.com' );
            if ( $updateText )
            {
                echo "Update: ".substr( $updateText, 0, 60 )."\n";

                $fakeUserName = substr( $this->faker->firstName(), 0, 1 ).". ".$this->faker->lastName();
                $insertDate = Functions::getCommentDate();

                $commentID = $exporter->addComment( $exporter->getCommentImportID( $complaint[ "{$type}_id" ], $type ), [
                    "complaint_id" => $toComplaintID,
                    "text"         => $updateText,
                    "is_update"    => false,
                    "date"         => $insertDate,
                    "user_name"   => $fakeUserName,
                    "user_date"   => date( "Y-m-d", strtotime( $insertDate ) - 60 ),
                    "import_data"  => [
                        "company_id"   => $this->vars['sourceCompanyRow'][ "company_id" ],
                        "{$type}_id" => $complaint[ "{$type}_id" ],
                        "company_url"  => $this->vars['sourceCompanyRow'][ "url" ],
                        "type"         => "{$type}-as-comment",
                        "scraper"      => $this->vars['importInfoScraper'],
                        "version"      => 1,
                    ],
                ] );
                if ( !$commentID )
                {
                    die( $exporter->getErrorsAsString() );
                }
            }
        }
    }
}