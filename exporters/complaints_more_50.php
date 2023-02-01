<?php
require __DIR__."/vendor/autoload.php";

use DataExport\Helpers\Db;
use DataExport\Exporters\CBExport;
use DataExport\Formatters\TextFormatter;
use DataExport\Data\BusinessData;
use DataExport\Helpers\CheckUniqueTextViaCSV;

$config = require __DIR__."/config.php";

##################################################################################

$profileName = "local";
#$profileName = "cb";
$profileAPI = $profileName === "local" ? "http://www.cb.local" : "https://www.complaintsboard.com";
$complaintType = "all"; # "review", "complaint", "all"
$removeBN = $profileName === "local"; # remove bn before try create new
$debugComplaintsAndReviews = false; # will remove all reviews & complaints and exit
$removeAllPosts = true; # before insert remove all old
$addComplaints = true; # without that no complaints or reviews will be added
$addOnly = 0; # if createAll and addOnly == country then create record or zero to always add
$maxCompanies = false;
$makeSpamComplaints = true; # may create not spamed complaints for fast insert
$makeScreenshot = true; # if no logo and website url exists and makeScreenshot == True try create screenshot
$checkTextInGoogle = false; #$profileName !== "local";

$checkUniqueViaCSV = new CheckUniqueTextViaCSV('check_texts.csv', 'check_texts_results.csv');
$checkUniqueViaCSV->setDisabledMode();

$importInfoScraper = "BBB Mustansir";
# Sergey posted this URL do not change
#$companyUrl = "https://www.bbb.org/us/az/scottsdale/profile/online-shopping/moonmandycom-1126-1000073935";
$companyUrls = [
    "https://www.bbb.org/us/ca/marina-del-rey/profile/razors/dollar-shave-club-inc-1216-100113835"
    /*"https://www.bbb.org/us/wa/yarrow-point/profile/pet-insurance/healthy-paws-pet-insurance-llc-1296-22528158",
    "https://www.bbb.org/us/ga/atlanta/profile/auto-diagnosis/fixd-automotive-inc-0443-27709950",
    "https://www.bbb.org/us/ca/san-francisco/profile/computer-software/discord-inc-1116-918699",
    "https://www.bbb.org/us/fl/orlando/profile/information-bureaus/checkpeople-llc-0733-90442795",
    "https://www.bbb.org/us/ca/commerce/profile/online-retailer/joybird-1216-1419900",
    "https://www.bbb.org/us/az/gilbert/profile/car-racing-equipment/vivid-racing-1126-27004033",
    "https://www.bbb.org/us/wi/chippewa-falls/profile/catalog-shopping/mason-companies-inc-0694-23003797",
    "https://www.bbb.org/us/ca/city-of-industry/profile/printer-sales-and-service/cyberpowerpc-1216-13080817",
    "https://www.bbb.org/us/ca/palo-alto/profile/computer-software/leetcode-1216-1276649",
    "https://www.bbb.org/us/co/denver/profile/newspaper/dp-media-network-llc-1296-13136",
    "https://www.bbb.org/us/ca/el-segundo/profile/vinyl-records/vnyl-1216-359687",
    "https://www.bbb.org/us/ca/los-angeles/profile/eyeglass-suppliers/lensabl-inc-1216-756759",
    "https://www.bbb.org/us/la/natchitoches/profile/online-travel-agency/bookvip-1015-90048356",
    "https://www.bbb.org/us/ca/san-francisco/profile/auto-renting-and-leasing/getaround-1116-390772",
    "https://www.bbb.org/us/ca/calabasas/profile/clothing/revice-denim-1216-714641",
    "https://www.bbb.org/us/ny/white-plains/profile/protective-covers/seal-skin-covers-0121-159372",
    "https://www.bbb.org/us/ca/gardena/profile/home-furnishings/ruggable-1216-893295",
    "https://www.bbb.org/us/ny/new-york/profile/cosmetics-sales/estee-lauder-companies-0121-2810",
    "https://www.bbb.org/us/ca/los-angeles/profile/jewelry-stores/edwin-novel-jewelry-design-1216-758547",
    "https://www.bbb.org/us/ca/san-francisco/profile/legal-forms/formswift-1116-463277",
    "https://www.bbb.org/us/co/englewood/profile/internet-service/rise-broadband-1296-90229187",
    "https://www.bbb.org/us/ca/redwood-city/profile/financial-services/bluevine-inc-1116-875531",
    "https://www.bbb.org/us/ca/marina-del-rey/profile/razors/dollar-shave-club-inc-1216-100113835",
    "https://www.bbb.org/us/ca/los-angeles/profile/designer-apparel/good-american-llc-1216-712189",
    "https://www.bbb.org/us/ca/cerritos/profile/retail-optical-goods/goggles4ucom-1216-100062313",
    "https://www.bbb.org/us/oh/wadsworth/profile/new-auto-parts/ecs-tuning-llc-0272-40000380",
    "https://www.bbb.org/us/ca/hayward/profile/bottles/larq-1116-896724",
    "https://www.bbb.org/us/il/chicago/profile/wholesale-health-products/factor-75-0654-90005442",
    "https://www.bbb.org/ca/ab/calgary/profile/credit-repair-services/debtless-credit-0017-118056",
    "https://www.bbb.org/us/ca/fremont/profile/electronics-and-technology/vava-1116-914331",
    "https://www.bbb.org/us/ca/cerritos/profile/drone-sales/dji-service-llc-1216-267337",
    "https://www.bbb.org/us/ca/hayward/profile/light-bulbs/xenonhidscom-1116-461865",
    "https://www.bbb.org/us/tx/austin/profile/laboratory-testing/everlywell-0825-1000175334",
    "https://www.bbb.org/us/fl/orlando/profile/antique-auto-parts/eckler-industries-inc-0733-90134991",
    "https://www.bbb.org/us/ca/burbank/profile/crowdfunding/startengine-crowdfunding-inc-1216-651625",
    "https://www.bbb.org/ca/ab/calgary/profile/airline-ticket-agency/swoop-0017-105000",
    "https://www.bbb.org/us/ca/san-francisco/profile/event-ticket-sales/gametime-united-inc-1116-874472",
    "https://www.bbb.org/us/co/denver/profile/oxygen/lpt-medical-inc-1296-90258714",
    "https://www.bbb.org/ca/ab/calgary/profile/credit-repair-services/credit-resources-0017-107546",
    "https://www.bbb.org/us/az/gilbert/profile/training-program/national-academy-of-sports-medicine-1126-1000015370",
    "https://www.bbb.org/us/co/colorado-springs/profile/heating-and-air-conditioning/air-pros-one-source-llc-0785-1000005324",
    "https://www.bbb.org/us/ca/berkeley/profile/organization/moveonorg-1116-897046",
    "https://www.bbb.org/us/ca/san-francisco/profile/extended-warranty-contract-service-companies/allstate-protection-plans-1116-35878",
    "https://www.bbb.org/us/ca/mountain-view/profile/financial-services/credit-sesame-inc-1216-1000006110",
    "https://www.bbb.org/us/ca/el-dorado-hills/profile/insurance-companies/blue-shield-of-california-1116-12019",
    "https://www.bbb.org/us/ca/los-angeles/profile/womens-clothing/emery-rose-1216-1527360",
    "https://www.bbb.org/us/ca/studio-city/profile/tax-consultant/tax-advocate-group-llc-1216-1266916",
    "https://www.bbb.org/us/co/centennial/profile/collections-agencies/lcs-financial-services-corporation-1296-90021710",
    "https://www.bbb.org/us/ca/san-francisco/profile/health-and-medical-products/hims-hers-inc-1116-880029",
    "https://www.bbb.org/us/pa/pittsburgh/profile/language-training-aids/duolingo-0141-71020747",
    "https://www.bbb.org/us/az/phoenix/profile/internet-marketing-services/staylisted-1126-1000030542",
    "https://www.bbb.org/us/il/lemont/profile/subscription-agents/discountmagscom-0654-88261175",
    "https://www.bbb.org/us/az/tucson/profile/online-travel-agency/bestairfarescom-1286-20094942",
    "https://www.bbb.org/us/nv/las-vegas/profile/airline-ticket-agency/flights-mojo-llc-1086-90056272",
    "https://www.bbb.org/us/ky/louisville/profile/online-shopping/cuddle-clones-llc-0402-159145672",
    "https://www.bbb.org/us/il/bolingbrook/profile/industrial-supply/power-equipment-direct-inc-0654-57001088",
    "https://www.bbb.org/us/ca/anaheim/profile/protective-covers/carcovercom-1126-1000073994",
    "https://www.bbb.org/us/ca/s-san-fran/profile/online-travel-agency/topbusinessclass-1116-548932",
    "https://www.bbb.org/us/ca/irvine/profile/boots/workbootsusacom-1126-172016064",
    "https://www.bbb.org/us/ca/walnut/profile/online-retailer/dreamcloud-1216-880731",
    "https://www.bbb.org/us/ny/new-york/profile/tv-program-distributors/dazn-group-ltd-0121-182459",
    "https://www.bbb.org/us/ca/oakland/profile/energy-service-company/ohmconnect-inc-1116-546548",
    "https://www.bbb.org/us/pa/blair-mills/profile/musical-instrument-manufacturers/drume-music-0141-71077866",
    "https://www.bbb.org/us/fl/fort-lauderdale/profile/insurance-companies/universal-property-casualty-insurance-company-0633-5003510",
    "https://www.bbb.org/us/fl/jacksonville/profile/new-auto-parts/nationwide-parts-distributors-inc-0403-9000575",
    "https://www.bbb.org/us/il/chicago/profile/credit-union/alliant-credit-union-0654-22003383",
    "https://www.bbb.org/us/ca/rch-cucamonga/profile/online-retailer/vevor-1066-850056466",
    "https://www.bbb.org/us/ca/redwood-city/profile/online-shopping/b-stock-supply-1116-383180",
    "https://www.bbb.org/us/ca/san-francisco/profile/online-gaming/skillz-inc-1116-460331",
    "https://www.bbb.org/us/ga/kennesaw/profile/loans/lendingpoint-llc-0443-27512115",
    "https://www.bbb.org/us/ca/redwood-city/profile/crowdfunding/gofundme-1116-876254",
    "https://www.bbb.org/us/ca/irvine/profile/financial-services/americor-1126-100093457",
    "https://www.bbb.org/us/tx/fort-worth/profile/moving-companies/simple-moving-labor-0825-163450866",
    "https://www.bbb.org/us/nc/winston-salem/profile/tobacco-manufacturers/rj-reynolds-tobacco-company-0503-2000053",
    "https://www.bbb.org/us/ca/tracy/profile/mattress-supplies/zinus-inc-1156-90044368",
    "https://www.bbb.org/us/nj/newark/profile/airlines/tap-portugal-0221-27000090",
    "https://www.bbb.org/us/ca/irvine/profile/computer-parts/replacement-laptop-keys-1126-100111246",
    "https://www.bbb.org/us/ca/compton/profile/auto-repair/tap-worldwide-llc-1216-13081573",
    "https://www.bbb.org/us/nh/nashua/profile/new-auto-parts/1a-auto-inc-0051-92051018",
    "https://www.bbb.org/us/ny/new-york/profile/airlines/el-al-israel-airlines-0121-7711",
    "https://www.bbb.org/us/al/birmingham/profile/grocery-delivery/shipt-0463-90146509",
    "https://www.bbb.org/us/ca/victorville/profile/car-dealers/victorville-chevrolet-cadillac-1066-850044930",
    "https://www.bbb.org/us/oh/hudson/profile/catalog-shopping/universal-screen-arts-inc-0272-35000112",
    "https://www.bbb.org/us/wi/pleasant-prairie/profile/pool-supplies/dohenys-llc-0694-4019043",
    "https://www.bbb.org/us/az/tempe/profile/real-estate-services/opendoor-1126-1000060421",
    "https://www.bbb.org/us/ca/san-diego/profile/market-research/branded-1126-172008213",
    "https://www.bbb.org/us/ut/american-fork/profile/womens-clothing/baltic-born-1166-90028660",
    "https://www.bbb.org/us/ca/fremont/profile/computer-parts/corsair-components-inc-1116-73436",
    "https://www.bbb.org/us/ca/san-diego/profile/military-gear/govx-1126-172006275",
    "https://www.bbb.org/us/ny/new-york/profile/pet-supplies/barkbox-0121-143591",
    "https://www.bbb.org/us/ut/provo/profile/tax-return-preparation/taxhawk-inc-1166-22009863",
    "https://www.bbb.org/us/az/tempe/profile/health-savings-administrators/solidarity-healthshare-1126-1000049616",
    "https://www.bbb.org/us/il/lincolnshire/profile/office-supplies/quillcom-0654-948",
    "https://www.bbb.org/us/ca/los-angeles/profile/soap/dr-squatch-inc-1216-1279759",
    "https://www.bbb.org/us/ca/oceanside/profile/online-retailer/soft-serve-clothing-1126-1000077699",
    "https://www.bbb.org/us/ca/redwood-city/profile/senior-delivery-services/because-market-1116-881197",
    "https://www.bbb.org/us/az/tempe/profile/loan-broker/freedomplus-1126-1000053878",
    "https://www.bbb.org/us/nj/hoboken/profile/manufactured-home-supplies/snow-joe-llc-0221-90100213",
    "https://www.bbb.org/us/fl/mary-esther/profile/major-appliance-parts/genuine-replacement-parts-0683-90040196",
    "https://www.bbb.org/us/ca/thousand-oaks/profile/cell-phone-supplies/red-pocket-mobile-1236-92011052",*/
];
$websiteUrls = [];
$websiteInstagramMedia = [];

##################################################################################

$profile = $config["dest"][ $profileName ];
if ( !is_array( $profile ) ) die( "Error: no profile data" );

echo "Creating source db...\n";
$srcDb = new Db();
$srcDb->connectOrDie( $config["source_db"]["host"], $config["source_db"]["user"], $config["source_db"]["pass"], $config["source_db"]["name"] );

echo "Creating dest db...\n";
$destDb = new Db();
$destDb->connectOrDie(  $profile["db"]["host"], $profile["db"]["user"], $profile["db"]["pass"], $profile["db"]["name"] );

##################################################################################

$companies = $srcDb->queryColumnArray("select company_id, count(*) cnt from complaint group by company_id having cnt > 50", "company_id" );
if ( !$companies ) die( "Query companies error: ".$srcDb->getExtendedError() );

$companyID2Url = [];

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
        $companyID2Url[$companyID] = $companyUrl;
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

    if (isset($companyID2Url[$companyId])) {
        echo "Url: ".$companyID2Url[$companyId]."\n";
    }

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
        continue;
    }

    $businessRow = $exporter->getBusiness($exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ]));
    if($businessRow["bname_instagram"] && 0) {
        echo "Add instagram media from ".$businessRow["bname_instagram"]." to BN...\n";

        $http = new GuzzleHttp\Client(['verify' => false, 'timeout' => 3600]);

        $url = $profileAPI.'/api/business/instagram-media?id='.$destBusinessID.'&do=load-media&token=jdf89jo343kgjs8gfds895jk3g';
        echo $url."\n";

        $response = $http->get($url);
        if ($response->getStatusCode() != 200) {
            echo 'Import instagram media error: '.$response->getBody()->getContents()."\n";
            exit;
        }
        $body = $response->getBody()->getContents();

        $json = json_decode($body);
        if(!$json) die(var_export($body,true)."\nJson decode fail\n");
        if (!$json->success) {
            echo "Instagram media error:\n";
            print_r($json->errors);
            exit;
        }
    }

    echo "Try add {$complaintType} in BN...\n";

    $csvFile = null;

    if ( $complaintType === "complaint" )
    {
        require __DIR__."/add-20-16-complaints.php";
    } elseif( $complaintType === "review" ) {
        require __DIR__."/add-20-16-reviews.php";
    } elseif( $complaintType === "all" ) {
        require __DIR__."/add-20-16-complaints.php";
        require __DIR__."/add-20-16-reviews.php";
    } else {
        die( "Unknown complain type: {$complaintType}" );
    }

    if ( $destBusinessID )
    {
        echo "Call update company & bn...\n";

        $exporter->callUpdateCompany( $destCompanyID );
        $exporter->callUpdateBusiness( $destBusinessID );

        $url = $profile["host"]."/asd-b".$destBusinessID.( $complaintType == "review" ? "/reviews" : "");

        $websiteUrls[] = $url;

        echo $url."\n";
    } else {
        echo "Removed all from company: ".$sourceCompanyRow["company_id"]."\n";
    }
}

$checkUniqueViaCSV->close();

print_r($websiteUrls);

echo "Script ends.\n";
