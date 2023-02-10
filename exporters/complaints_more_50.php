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
$addComplaintsToPublicBN = true;
$isDisableBusiness = true;
$removeBN = $profileName === "local"; # remove bn before try create new
$debugComplaintsAndReviews = false; # will remove all reviews & complaints and exit
$removeAllPosts = true; # before insert remove all old
$addComplaints = true; # without that no complaints or reviews will be added
$addOnly = 0; # if createAll and addOnly == country then create record or zero to always add
$maxCompanies = false;
$makeSpamComplaints = false; # may create not spamed complaints for fast insert
$makeScreenshot = true; # if no logo and website url exists and makeScreenshot == True try create screenshot
$checkTextInGoogle = $profileName !== "local";

$checkUniqueViaCSV = new CheckUniqueTextViaCSV('check_texts.csv', 'check_texts_results.csv');
$checkUniqueViaCSV->setDisabledMode();

$importInfoScraper = "BBB Mustansir";
# Sergey posted this URL do not change
#$companyUrl = "https://www.bbb.org/us/az/scottsdale/profile/online-shopping/moonmandycom-1126-1000073935";
$companyUrls = [
    "https://www.bbb.org/us/il/chicago/profile/credit-reporting-agencies/trans-union-llc-0654-2713",
    /*"https://www.bbb.org/us/ca/san-jose/profile/payment-processing-services/venmo-1216-634567",
    "https://www.bbb.org/us/ca/manhattan-beach/profile/internet-service/prodege-llc-1216-100088742",
    "https://www.bbb.org/us/mo/saint-peters/profile/auto-service-contract-companies/carshield-0734-310030296",
    "https://www.bbb.org/us/in/indianapolis/profile/contractor-referral/angi-0382-3041007",
    "https://www.bbb.org/us/ca/san-francisco/profile/auto-renting-and-leasing/turo-1116-378793",
    "https://www.bbb.org/us/co/englewood/profile/internet-providers/viasat-inc-1296-9036631",
    "https://www.bbb.org/us/ca/los-angeles/profile/event-ticket-sales/axs-1216-100111549",
    "https://www.bbb.org/us/ma/boston/profile/online-gaming/draftkings-inc-0021-134635",
    "https://www.bbb.org/us/ny/new-york/profile/cosmetics-sales/il-makiage-0121-9390",
    "https://www.bbb.org/us/ca/los-angeles/profile/online-retailer/goat-1216-704262",
    "https://www.bbb.org/us/az/phoenix/profile/cable-tv/cox-communications-inc-1126-3655",
    "https://www.bbb.org/us/nj/edison/profile/home-warranty-plans/serviceplus-home-warranty-0221-90194173",
    "https://www.bbb.org/us/ca/san-francisco/profile/hotel-reservation/snaptravel-1116-881071",
    "https://www.bbb.org/us/ca/walnut/profile/counseling/cerebral-1216-1532400",
    "https://www.bbb.org/us/ca/menlo-park/profile/games/meta-store-1116-874563",
    "https://www.bbb.org/us/az/scottsdale/profile/cbd-oil/purekana-1126-1000050481",
    "https://www.bbb.org/us/ny/new-york/profile/weight-loss/calibrate-health-inc-0121-87146034",
    "https://www.bbb.org/us/ca/san-francisco/profile/loans/prospercom-1116-118427",
    "https://www.bbb.org/ca/on/windsor/profile/online-retailer/cook-store-inc-0187-1066961",
    "https://www.bbb.org/us/ca/san-francisco/profile/employment-background-check/checkr-inc-1116-539357",
    "https://www.bbb.org/us/nj/fairfield/profile/online-shopping/ontel-products-corp-0221-29000524",
    "https://www.bbb.org/us/ma/medford/profile/roadside-assistance/agero-0021-3395",
    "https://www.bbb.org/us/ca/santa-ana/profile/tax-return-preparation/optima-tax-relief-1126-100115586",
    "https://www.bbb.org/us/ca/culver-city/profile/retail-shoes/flight-club-1216-100048299",
    "https://www.bbb.org/us/ca/san-francisco/profile/birth-control-information/nurx-1116-880452",
    "https://www.bbb.org/us/ca/irvine/profile/online-retailer/all-things-by-faith-1126-172020506",
    "https://www.bbb.org/us/de/lewes/profile/event-ticket-sales/tickets-centercom-0251-92012097",
    "https://www.bbb.org/us/sc/columbia/profile/gun-dealers/palmetto-state-armory-0663-34084856",
    "https://www.bbb.org/us/ca/larkspur/profile/financial-services/uphold-hq-inc-1116-879439",
    "https://www.bbb.org/us/az/scottsdale/profile/telecommunications/nextiva-inc-1126-97030201",
    "https://www.bbb.org/ca/ab/calgary/profile/credit-repair-services/credit-value-0017-118041",
    "https://www.bbb.org/us/nj/delanco/profile/ecommerce/misfits-market-0221-90194397",
    "https://www.bbb.org/us/ca/irvine/profile/tax-negotiators/tax-rise-inc-1126-172021357",
    "https://www.bbb.org/us/il/chicago/profile/musical-instrument-supplies-and-accessories/reverbcom-llc-0654-88654144",
    "https://www.bbb.org/us/ca/beverly-hills/profile/skin-care/laseraway-medical-group-1216-100040419",
    "https://www.bbb.org/us/nv/las-vegas/profile/electronic-cigarettes/eightvape-1086-90042688",
    "https://www.bbb.org/us/ca/san-francisco/profile/payroll-services/gusto-1116-451512",
    "https://www.bbb.org/us/ca/los-angeles/profile/pet-supplies/prettylitter-1216-629436",
    "https://www.bbb.org/us/ca/thousand-oaks/profile/mortgage-lenders/amerihome-mortgage-company-llc-1236-92029856",
    "https://www.bbb.org/us/ma/boston/profile/burglar-alarm-systems/simplisafe-inc-0021-129235",
    "https://www.bbb.org/us/ny/new-york/profile/tv-stations/amc-networks-inc-0121-124912",
    "https://www.bbb.org/us/fl/pembroke-pines/profile/cosmetics-sales/boxy-charm-inc-0633-90122637",
    "https://www.bbb.org/us/ca/irvine/profile/information-technology-services/setschedule-1126-172013479",
    "https://www.bbb.org/us/ca/san-francisco/profile/medical-consultants/done-1116-923937",
    "https://www.bbb.org/us/ca/los-angeles/profile/online-retailer/boohoocom-usa-inc-1216-1266564",
    "https://www.bbb.org/us/ma/cambridge/profile/internet-marketing-services/everquote-inc-0021-122911",
    "https://www.bbb.org/us/ca/alhambra/profile/tobacco-store/element-vape-1216-413453",
    "https://www.bbb.org/us/ny/new-york/profile/security-consultant/clear-0121-149432",
    "https://www.bbb.org/ca/on/markham/profile/heating-and-air-conditioning/enercare-home-commercial-services-limited-partnership-0107-1322888",
    "https://www.bbb.org/us/md/savage/profile/roofing-contractors/long-home-products-0011-20014094",
    "https://www.bbb.org/us/ca/san-diego/profile/debt-relief-services/beyond-finance-1126-1000082863",
    "https://www.bbb.org/us/md/baltimore/profile/heating-and-air-conditioning/constellation-home-products-services-llc-0011-23010666",
    "https://www.bbb.org/us/ca/san-francisco/profile/diamond/brilliant-earth-llc-1116-154721",
    "https://www.bbb.org/ca/ab/calgary/profile/financial-services/plastk-financial-rewards-inc-0017-115524",
    "https://www.bbb.org/us/oh/valley-city/profile/lawn-mower/mtd-products-inc-0272-13000202",
    "https://www.bbb.org/us/fl/fort-lauderdale/profile/cruises/msc-cruises-inc-0633-14001025",
    "https://www.bbb.org/ca/on/richmond-hill/profile/travel-agency/utovacation-0107-1313842",
    "https://www.bbb.org/us/ca/santa-fe-springs/profile/wigs/unice-hair-1216-645869",
    "https://www.bbb.org/us/ca/irvine/profile/auto-warranty-plans/ox-car-care-1126-172015721",
    "https://www.bbb.org/us/ca/fresno/profile/digital-marketing/rewardbee-llc-1066-850061379",
    "https://www.bbb.org/us/de/wilmington/profile/bank/barclays-bank-delaware-0251-22002677",
    "https://www.bbb.org/us/ca/fresno/profile/gift-cards/bperx-llc-1066-850037289",
    "https://www.bbb.org/us/ca/culver-city/profile/womens-clothing/skims-1216-1265584",
    "https://www.bbb.org/ca/on/etobicoke/profile/collections-agencies/veritas-alliance-incorporated-0107-1340449",
    "https://www.bbb.org/us/ny/new-york/profile/online-retailer/mpb-us-inc-0121-174100",
    "https://www.bbb.org/us/tx/austin/profile/delivery-service/x-delivery-0825-1000195076",
    "https://www.bbb.org/us/ok/oklahoma-city/profile/electronic-cigarettes/perfect-vape-llc-0995-90042277",
    "https://www.bbb.org/us/ca/newark/profile/computer-hardware/logitech-inc-1116-71823",
    "https://www.bbb.org/us/ca/los-angeles/profile/publishers-magazine/high-times-1216-1077588",
    "https://www.bbb.org/ca/bc/vancouver/profile/collections-agencies/general-credit-services-inc-0037-101325",
    "https://www.bbb.org/us/ia/cedar-rapids/profile/digital-marketing/hibu-inc-0664-32057924",
    "https://www.bbb.org/us/nj/warren/profile/market-survey/lightspeed-llc-0221-17002982",
    "https://www.bbb.org/ca/on/toronto/profile/financing/flexiti-financial-inc-0107-1336765",
    "https://www.bbb.org/us/ga/atlanta/profile/real-estate-investing/cortland-0443-27301288",
    "https://www.bbb.org/us/ca/el-cajon/profile/solar-energy-contractors/semper-solaris-construction-inc-1126-172005700",
    "https://www.bbb.org/us/ca/mountain-view/profile/online-education/coursera-inc-1216-355709",
    "https://www.bbb.org/ca/on/toronto/profile/financial-services/wave-financial-inc-0107-1281912",
    "https://www.bbb.org/us/ny/new-york/profile/online-retailer/teepublic-0121-168669",
    "https://www.bbb.org/us/ny/new-york/profile/cryptocurrency-exchange/voyager-digital-llc-0121-87148788",
    "https://www.bbb.org/us/ga/marietta/profile/home-warranty-plans/afc-home-club-0443-27282410",
    "https://www.bbb.org/us/in/indianapolis/profile/moving-brokers/nationwide-moving-and-storage-llc-0382-90039589",
    "https://www.bbb.org/us/ri/cranston/profile/lift-kits/tasca-parts-center-0021-234350",
    "https://www.bbb.org/us/az/scottsdale/profile/home-builders/taylor-morrison-1126-92004815",
    "https://www.bbb.org/us/nd/belcourt/profile/payday-loans/spotloan-0704-96368067",
    "https://www.bbb.org/us/ny/new-york/profile/online-auctions/worthycom-0121-149680",
    "https://www.bbb.org/us/ga/atlanta/profile/clothing/asos-ltd-0443-27404172",
    "https://www.bbb.org/us/ca/san-francisco/profile/document-scanning-service/docusign-inc-1116-447881",
    "https://www.bbb.org/us/in/carmel/profile/online-retailer/parker-gwen-0382-90024170",
    "https://www.bbb.org/us/va/henrico/profile/property-insurance/elephant-insurance-services-llc-0603-63394765",
    "https://www.bbb.org/us/ny/new-york/profile/designer-apparel/supreme-0121-101683",
    "https://www.bbb.org/us/ca/escondido/profile/vacation-timeshare/welk-resort-group-inc-1126-100406",
    "https://www.bbb.org/us/ny/new-york/profile/telemedicine/rex-md-0121-87148687",
    "https://www.bbb.org/us/ca/santa-monica/profile/metal-art/fine-art-america-1216-100120505",
    "https://www.bbb.org/us/ca/irvine/profile/auto-warranty-plans/palisade-protection-group-1126-1000082764",
    "https://www.bbb.org/us/il/chicago/profile/parking-facilities/spothero-0654-88576696",
    "https://www.bbb.org/us/nj/mahwah/profile/auto-manufacturers/volvo-cars-north-america-llc-0221-29002860",
    "https://www.bbb.org/us/al/fairhope/profile/insurance-companies/trawick-international-inc-0463-235958510",
    "https://www.bbb.org/us/ca/los-angeles/profile/business-consultant/seek-capital-llc-1216-356029",*/
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
/*
$cb = new CBExport($destDb, "");
var_dump($cb->isCategoryExists("parent 111"));
var_dump($cb->isCategoryExists("parent 222"));
var_dump($cb->isCategoryExists("parent 222", "child 222"));
var_dump($cb->isCategoryExists("parent 222", "child 333"));
exit;
var_dump($cb->addCategory([
   'name' => 'parent 111',
   "import_data" => [
       "version"      => 1,
   ],
]),$cb->getErrorsAsString());

var_dump($cb->addCategory([
    'name' => 'parent 222',
    'child_name' => 'child 222',
    "import_data" => [
        "version"      => 1,
    ],
]),$cb->getErrorsAsString());

exit;
*/
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
    echo "{$companyNbr}/".count($companies).") Company: {$companyId}\n";

    if( $maxCompanies > 0 && $companyNbr >= $maxCompanies )
    {
        echo "Max companies, break\n";
        break;
    }

    $sourceCompanyRow = $srcDb->selectRow( "*", "company", [ "company_id" => $companyId, 'half_scraped' => 0 ] );
    if ( !$sourceCompanyRow ) die( "Error: ".$srcDb->getExtendedError() );

    #####################################################################

    if (isset($companyID2Url[$companyId])) {
        echo "{$companyNbr}/".count($companies).") Url: ".$companyID2Url[$companyId]."\n";
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

    [ $destBusinessID, $destCompanyID ] = BusinessData::create( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper, $makeScreenshot, $isDisableBusiness );

    if ( !$addComplaintsToPublicBN && $exporter->isBusinessActive( $exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ]) ) ) {
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
