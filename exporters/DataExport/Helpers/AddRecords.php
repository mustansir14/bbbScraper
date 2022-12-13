<?php

namespace DataExport\Helpers;

use DataExport\Formatters\TextFormatter;

class AddRecords
{
    private array $vars;
    private $faker;

    public function __construct($vars)
    {
        $this->vars = $vars;
        $this->faker = \Faker\Factory::create();

        foreach( ['companyNameWithoutAbbr','exporter','isInsert','destCompanyID','destBusinessID','sourceCompanyRow','importInfoScraper','makeSpamComplaints','counter'] as $name ) {
            if ( !array_key_exists( $name, $this->vars ) || empty( $this->vars[$name]) ) {
                die( "Error: key {$name} not exists in vars" );
            }
        }

        $this->counter = $this->vars['counter'];
    }
    
    private function addComplaint( object $exporter, array $complaint )
    {
        $complaintText = TextFormatter::fixText( $complaint["complaint_text"], 'complaintsboard.com' );
        if ( $complaintText )
        {
            echo ($this->counter++).") ({$complaint['complaint_id']}) ".$complaint[ "complaint_date" ].": ".substr( $complaintText, 0, 60 )."...\n";

            $lines = explode( ".", $complaint[ "complaint_text" ] );
            $subject = "";
            foreach ( $lines as $line )
            {
                $subject .= $line.". ";
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
                $updateText = TextFormatter::fixText( $complaint["company_response_text"], 'complaintsboard.com' );
                if ( $updateText ) {
                    $resolvedDate = $complaint[ "company_response_date" ];
                }
            }

            $fakeUserName = substr( $this->faker->firstName(), 0, 1 ).". ".$this->faker->lastName();
            $complaintID = $exporter->addComplaint( $exporter->getComplaintImportID( $complaint[ "complaint_id" ] ), [
                "company_id"  => $this->vars['destCompanyID'],
                "subject"     => $subject,
                "text"        => $complaintText,
                "type"        => $complaint["type"],
                "date"        => $complaint[ "complaint_date" ],
                "user_name"   => $fakeUserName,
                "user_date"   => date( "Y-m-d", strtotime( $complaint[ "complaint_date" ] ) - 60 ),
                "is_resolved"  => $resolvedDate ?: 0,
                "resolved_date" => $resolvedDate ?: null,
                "isOpen"      => 1,
                "import_data" => [
                    "company_id"   => $this->vars['sourceCompanyRow'][ "company_id" ],
                    "complaint_id" => $complaint[ "complaint_id" ],
                    "company_url"  => $this->vars['sourceCompanyRow'][ "url" ],
                    "type"         => "complaint",
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
                    $exporter->getComplaintImportID( $complaint[ "complaint_id" ] ),
                    basename( __FILE__ ).": make private"
                );
            }
            else
            {
                $exporter->unspamComplaint( $exporter->getComplaintImportID( $complaint[ "complaint_id" ] ) );
            }

            return $complaintID;
        }

        return 0;
    }

    private function addResponse( object $exporter, array $complaint, int $complaintID )
    {
        if ( $complaint["company_response_text"] )
        {
            $userName = "{$this->vars['companyNameWithoutAbbr']} Support";

            $updateText = TextFormatter::fixText( $complaint["company_response_text"], 'complaintsboard.com' );
            if ( $updateText )
            {
                echo "Update: ".substr( $updateText, 0, 60 )."\n";

                $commentID = $exporter->addComment( $exporter->getCommentImportID( $complaint[ "complaint_id" ] ), [
                    "complaint_id" => $complaintID,
                    "text"         => $updateText,
                    "is_update"    => true,
                    "date"         => $complaint[ "company_response_date" ],
                    "user_name"    => $userName,
                    "user_date"    => date( "Y-m-d", strtotime( $complaint[ "company_response_date" ] ) - 1 * 365 * 24 * 3600 ),
                    "user_email"   => $this->faker->email(),
                    "user_support" => $this->vars['destBusinessID'],
                    "import_data"  => [
                        "company_id"   => $this->vars['sourceCompanyRow'][ "company_id" ],
                        "complaint_id" => $complaint[ "complaint_id" ],
                        "company_url"  => $this->vars['sourceCompanyRow'][ "url" ],
                        "type"         => "complaint-response",
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

    public function insertComplaint( array $complaint ): int
    {
        $exporter = $this->vars['exporter'];

        if ( $this->vars['isInsert'] ) {
            $complaintID = $this->addComplaint( $exporter, $complaint );
            if ( $complaintID )
            {
                $this->addResponse( $exporter, $complaint, $complaintID );

                $exporter->callUpdateComplaint( $complaintID );
            }

            return $complaintID;
        }

        return 0;
    }

    public function insertAsComment( array $complaint, int $toComplaintID )
    {
        $exporter = $this->vars['exporter'];

        if ( $this->vars['isInsert'] ) {
            $userName = "{$this->vars['companyNameWithoutAbbr']} Support";

            $updateText = TextFormatter::fixText( $complaint["complaint_text"], 'complaintsboard.com' );
            if ( $updateText )
            {
                echo "Update: ".substr( $updateText, 0, 60 )."\n";

                $fakeUserName = substr( $this->faker->firstName(), 0, 1 ).". ".$this->faker->lastName();

                $commentID = $exporter->addComment( $exporter->getCommentImportID( $complaint[ "complaint_id" ] ), [
                    "complaint_id" => $toComplaintID,
                    "text"         => $updateText,
                    "is_update"    => false,
                    "date"         => $complaint[ "complaint_date" ],
                    "user_name"   => $fakeUserName,
                    "user_date"   => date( "Y-m-d", strtotime( $complaint[ "complaint_date" ] ) - 60 ),
                    "import_data"  => [
                        "company_id"   => $this->vars['sourceCompanyRow'][ "company_id" ],
                        "complaint_id" => $complaint[ "complaint_id" ],
                        "company_url"  => $this->vars['sourceCompanyRow'][ "url" ],
                        "type"         => "complaint-as-comment",
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