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
$removeBN = false;
$removeAllPosts = true;
$addComplaints = true;
$addOnly = 0; # if createAll and addOnly == country then create record or zero to always add
$maxCompanies = false;
$makeSpamComplaints = true;
$makeScreenshot = $profileName !== "local";
$importInfoScraper = "BBB Mustansir";
# Sergey posted this URL do not change
#$companyUrl = "https://www.bbb.org/us/az/scottsdale/profile/online-shopping/moonmandycom-1126-1000073935";
$companyUrls = [
    #"https://www.bbb.org/us/wi/monroe/profile/catalog-shopping/colony-brands-inc-0694-22000113",
    #"https://www.bbb.org/us/ca/san-francisco/profile/computer-hardware/fitbit-inc-1116-380612",
    #"https://www.bbb.org/us/fl/orlando/profile/event-ticket-sales/entertainment-benefits-group-llc-0733-233704229",
    #"https://www.bbb.org/us/oh/columbus/profile/credit-cards-and-plans/comenity-capital-bank-0302-70009182",
    #"https://www.bbb.org/us/nv/las-vegas/profile/credit-cards-and-plans/credit-one-bank-1086-48541",
    #"https://www.bbb.org/us/ny/rochester/profile/clothing/fairyseasoncom-0041-235987200",
    #"https://www.bbb.org/us/ca/santa-clara/profile/textbooks/cheggcom-1216-238456",
    #"https://www.bbb.org/us/ca/los-angeles/profile/online-retailer/farfetch-1216-264428",
    #"https://www.bbb.org/us/pa/coraopolis/profile/sporting-goods-retail/dicks-sporting-goods-inc-0141-16001055",
    "https://www.bbb.org/us/ca/los-angeles/profile/fashion-accessories/fabfitfun-inc-1216-1004302",
];
$websiteUrls = [];

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

    if ( $removeAllPosts )
    {
        BusinessData::removeAllPosts( $exporter, $sourceCompanyRow, $complaintType );
    }

    [ $destBusinessID, $destCompanyID ] = BusinessData::create( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper, $makeScreenshot, $makeSpamComplaints );

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

        $url = $profile["host"]."/asd-b".$destBusinessID;

        $websiteUrls[] = $url;

        echo $url."\n";
    } else {
        echo "Removed all from company: ".$sourceCompanyRow["company_id"]."\n";
    }
}

print_r($websiteUrls);

echo "Script ends.\n";
