<?php
use DataExport\Helpers\AddComplaint;

#####################################################################

$limit = 500;
$offset = 0;
$fromID = -1;
$skip = 0;
$counter = 0;
$faker = Faker\Factory::create();

while ( $addComplaints )
{
    $complaints = $srcDb->selectArray(
        "*",
        "complaint",
        "company_id = {$sourceCompanyRow["company_id"]}",
        false,
        "complaint_date",
        sprintf( "%d,%d", $offset, $limit )
    );
    if ( $complaints === false ) die( $srcDb->getExtendedError() );
    if ( !$complaints ) break;

    $offset += count( $complaints );

    echo $srcDb->getSQL()."\n";

    foreach( $complaints as $complaint )
    {
        $counter++;
        if ( $counter < $skip ) continue;

        $fromID = $complaint["complaint_id"];
        $isInsert = $createAll && ( $addOnly < 1 || $addOnly === $counter );

        $helper = new AddRecords([
            'counter' => $counter,
            'isInsert' => $isInsert,
            'companyNameWithoutAbbr' => $companyNameWithoutAbbr,
            'removeComments' => $removeComments,
            'removeComplaints' => $removeComplaints,
            'exporter' => $exporter,
            'destCompanyID' => $destCompanyID,
            'destBusinessID' => $destBusinessID,
            'sourceCompanyRow' => $sourceCompanyRow,
            'importInfoScraper' => $importInfoScraper,
            'isDisableComplaints' => $isDisableComplaints,
        ]);
        $helper->insertComplaint($complaint);

        /*if ( $removeComplaints )
        {
            echo "Remove complaint: ".$complaint["complaint_id"]."\n";

            if ( !$exporter->removeComplaintByImportID( $exporter->getComplaintImportID( $complaint["complaint_id"])) )
            {
                die( $exporter->getErrorsAsString() );
            }
        }

        if ( $isInsert )
        {
            $complaintText = TextFormatter::fixText( $complaint["complaint_text"], 'complaintsboard.com' );
            if ( $complaintText )
            {
                echo $counter.") ({$complaint['complaint_id']}) ".$complaint[ "complaint_date" ].": ".substr( $complaintText, 0, 60 )."...\n";
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
                $fakeUserName = substr( $faker->firstName(), 0, 1 ).". ".$faker->lastName();
                $complaintID = $exporter->addComplaint( $exporter->getComplaintImportID( $complaint[ "complaint_id" ] ), [
                    "company_id"  => $destCompanyID,
                    "subject"     => $subject,
                    "text"        => $complaintText,
                    "date"        => $complaint[ "complaint_date" ],
                    "user_name"   => $fakeUserName,
                    "user_date"   => date( "Y-m-d", strtotime( $complaint[ "complaint_date" ] ) - 60 ),
                    "isOpen"      => 1,
                    "import_data" => [
                        "company_id"   => $sourceCompanyRow[ "company_id" ],
                        "complaint_id" => $complaint[ "complaint_id" ],
                        "company_url"  => $sourceCompanyRow[ "url" ],
                        "type"         => "complaint",
                        "scraper"      => $importInfoScraper,
                        "version"      => 1,
                    ],
                ] );
                if ( !$complaintID )
                {
                    die( $exporter->getErrorsAsString() );
                }
                if ( $makeSpamComplaints )
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
            }
        }

        if ( $complaint["company_response_text"] )
        {
            $userName = "{$companyNameWithoutAbbr} Support";

            if ( $removeComments )
            {
                echo "Remove comment: ".$complaint["complaint_id"]."\n";

                if ( !$exporter->removeCommentByImportID( $exporter->getCommentImportID( $complaint["complaint_id"] ) ) )
                {
                    die( $exporter->getErrorsAsString() );
                }
            }

            if ( $isInsert )
            {
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
                        "user_email"   => $faker->email(),
                        "user_support" => $destBusinessID,
                        "import_data"  => [
                            "company_id"   => $sourceCompanyRow[ "company_id" ],
                            "complaint_id" => $complaint[ "complaint_id" ],
                            "company_url"  => $sourceCompanyRow[ "url" ],
                            "type"         => "complaint-response",
                            "scraper"      => $importInfoScraper,
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

        if ( $isInsert )
        {
            $exporter->callUpdateComplaint( $complaintID );
        }*/
    }
}