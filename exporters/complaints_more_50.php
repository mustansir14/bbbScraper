<?php
require __DIR__."/vendor/autoload.php";

use DataExport\Helpers\Db;
use DataExport\Exporters\CBExport;
use DataExport\Formatters\TextFormatter;
use DataExport\Data\BusinessData;

$config = require __DIR__."/config.php";

##################################################################################

$profileName = "local";
#$profileName = "cb";
$profileAPI = $profileName === "local" ? "http://www.cb.local" : "https://www.complaintsboard.com";
$complaintType = 1 ? "review" : "complaint";
$removeBN = false; # remove bn before try create new
$debugComplaintsAndReviews = false; # will remove all reviews & complaints and exit
$removeAllPosts = true; # before insert remove all old
$addComplaints = true; # without that no complaints or reviews will be added
$addOnly = 0; # if createAll and addOnly == country then create record or zero to always add
$maxCompanies = false;
$makeSpamComplaints = true; # may create not spamed complaints for fast insert
$makeScreenshot = $profileName !== "local"; # if no logo and website url exists and makeScreenshot == True try create screenshot
$checkTextInGoogle = false; #$profileName !== "local";
$importInfoScraper = "BBB Mustansir";
# Sergey posted this URL do not change
#$companyUrl = "https://www.bbb.org/us/az/scottsdale/profile/online-shopping/moonmandycom-1126-1000073935";
$companyUrls = [
    #"https://www.bbb.org/us/az/phoenix/profile/home-services/george-brazil-plumbing-electrical-1126-5000904",
    #"https://www.bbb.org/us/az/phoenix/profile/pool-supplies/wild-west-pool-supplies-llc-1126-1000036991",
    "https://www.bbb.org/us/ca/city-of-industry/profile/party-supplies/tableclothsfactorycom-1216-100104360",
    #"https://www.bbb.org/us/ca/benicia/profile/online-shopping/blendjet-1116-882016",
    #"https://www.bbb.org/us/ca/chatsworth/profile/online-retailer/city-beauty-1216-718336",
    #"https://www.bbb.org/us/wi/appleton/profile/wheels/custom-offsets-llc-0694-1000017885",
    #"https://www.bbb.org/us/ca/beverly-hills/profile/online-cosmetic-sales/beverly-hills-md-1216-356713",
    #"https://www.bbb.org/us/mn/north-mankato/profile/masquerade-costumes/halloween-costumescom-0704-96001483",
    #"https://www.bbb.org/us/mi/ferndale/profile/new-auto-parts/detroit-axle-0332-90015722",
    #"https://www.bbb.org/us/fl/largo/profile/canes/fashionable-canes-hats-0653-18002096",
];
$websiteUrls = [];
$websiteInstagramMedia = [];

##################################################################################

$profile = $config["dest"][ $profileName ];
if ( !is_array( $profile ) ) die( "Error: no profile data" );

$srcDb = new Db();
$srcDb->connectOrDie( $config["source_db"]["host"], $config["source_db"]["user"], $config["source_db"]["pass"], $config["source_db"]["name"] );

$destDb = new Db();
$destDb->connectOrDie(  $profile["db"]["host"], $profile["db"]["user"], $profile["db"]["pass"], $profile["db"]["name"] );

##################################################################################

$companies = $srcDb->queryColumnArray("select company_id, count(*) cnt from complaint group by company_id having cnt > 50", "company_id" );
if ( !$companies ) die( "Query companies error: ".$srcDb->getExtendedError() );

# ONLY FOR TESTING, IN RELEASE MUST BE REMOVED
if ( $companyUrls ) {
    $companies = [];

    foreach( $companyUrls as $companyUrl )
    {
        $companyID = $srcDb->queryColumnRow( "select company_id from company where url = '".$srcDb->escape( $companyUrl )."'", "company_id" );
        if ( !$companyID )
        {
            die( "No company url: ".$srcDb->getExtendedError() );
        }

        $companies[] = $companyID;
    }
}

$exporter = new CBExport( $destDb, $profileAPI );

echo "Starting export...\n";

foreach( $companies as $companyNbr => $companyId )
{
    echo "Company: {$companyId}\n";

    if( $maxCompanies > 0 && $companyNbr >= $maxCompanies )
    {
        echo "Max companies, break\n";
        break;
    }

    $sourceCompanyRow = $srcDb->selectRow( "*", "company", [ "company_id" => $companyId, 'half_scraped' => 0 ] );
    if ( !$sourceCompanyRow ) die( "Error: ".$srcDb->getExtendedError() );

    #####################################################################

    $destCompanyID = 0;
    $destBusinessID = 0;
    $companyNameOriginal = $sourceCompanyRow[ "company_name" ];
    $companyNameWithoutAbbr = TextFormatter::removeAbbreviationsFromCompanyName( $sourceCompanyRow[ "company_name" ] );

    #####################################################################

    if ( $removeBN )
    {
        BusinessData::remove( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr );
    }

    # for debug only
    if ( $debugComplaintsAndReviews ) {
        BusinessData::removeAllPosts( $exporter, $sourceCompanyRow, "complaint" );
        BusinessData::removeAllPosts( $exporter, $sourceCompanyRow, "review" );

        echo "All imported complaints & comments removed\n";
        exit;
    }

    if ( $removeAllPosts )
    {
        BusinessData::removeAllPosts( $exporter, $sourceCompanyRow, $complaintType );
    }

    [ $destBusinessID, $destCompanyID ] = BusinessData::create( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper, $makeScreenshot, $makeSpamComplaints );

    if ( $exporter->isBusinessActive( $exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ]) ) ) {
        echo "Stop: business profile is active, may be already records changed!\n";
        exit;
    }

    if ( $complaintType === "complaint" )
    {
        #require __DIR__."/add-all-complaints.php";
        require __DIR__."/add-20-16-complaints.php";
    } elseif( $complaintType === "review" ) {
        require __DIR__."/add-20-16-reviews.php";
    } else {
        die( "Unknown complain type: {$complaintType}" );
    }

    if ( $destBusinessID )
    {
        $exporter->callUpdateCompany( $destCompanyID );
        $exporter->callUpdateBusiness( $destBusinessID );

        $url = $profile["host"]."/asd-b".$destBusinessID.( $complaintType == "review" ? "/reviews" : "");

        $websiteUrls[] = $url;
        $websiteInstagramMedia[] = "php cron.php LoadInstagramMedia {$destBusinessID}";

        echo $url."\n";
    } else {
        echo "Removed all from company: ".$sourceCompanyRow["company_id"]."\n";
    }
}

print_r($websiteUrls);

echo "DO NOT FORGET ADD MEDIA TO WEBSITE\n\n";
echo implode( "\n", $websiteInstagramMedia)."\n\n";

echo "Script ends.\n";
