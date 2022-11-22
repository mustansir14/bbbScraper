<?php
require __DIR__."/vendor/autoload.php";

use DataExport\Helpers\Db;
use DataExport\Helpers\BBBAPIHelper;
use DataExport\Exporters\CBExport;
use DataExport\Formatters\TextFormatter;
use DataExport\Formatters\PhoneFormatter;
use DataExport\Formatters\WebFormatter;
use DataExport\Formatters\HoursFormatter;

$config = require __DIR__."/config.php";

##################################################################################

$profileName = "local";
$profileName = "cb";
$profileAPI = $profileName === "local" ? "http://www.cb.local" : "https://www.complaintsboard.com";
$removeBN = $profileName === "local" || 1; # set true if need remove all records from dba
$removeFAQ = true;
$removeComplaints = true;
$removeComments = true;
$createAll = true; # set true if need add new records
$addComplaints = true;
$addOnly = 0; # if createAll and addOnly == country then create record or zero to always add
$maxCompanies = false;
$makeSpamComplaints = true;
$importInfoScraper = "BBB Mustansir";
# Sergey posted this URL do not change
#$companyUrl = "https://www.bbb.org/us/az/scottsdale/profile/online-shopping/moonmandycom-1126-1000073935";
$companyUrls = [
    "https://www.bbb.org/us/ca/san-francisco/profile/mobile-apps/cash-app-1116-919908",
    /*"https://www.bbb.org/us/wa/seattle/profile/ecommerce/amazoncom-1296-7039385",
    "https://www.bbb.org/us/in/indianapolis/profile/catalog-shopping/full-beauty-brands-0382-1809",
    "https://www.bbb.org/us/ca/calabasas/profile/online-retailer/yeezy-supply-1216-717168",
    "https://www.bbb.org/us/or/portland/profile/mobile-phone-service/consumer-cellular-1296-74003110",
    "https://www.bbb.org/us/il/niles/profile/collectibles/the-bradford-exchange-ltd-0654-136",
    "https://www.bbb.org/us/ca/san-francisco/profile/computer-hardware/fitbit-inc-1116-380612",
    "https://www.bbb.org/us/ca/san-francisco/profile/internet-providers/paramount-1116-27331",
    "https://www.bbb.org/us/tx/austin/profile/prepaid-debit-cards/netspend-corporation-0825-53229",
    "https://www.bbb.org/us/wi/monroe/profile/catalog-shopping/colony-brands-inc-0694-22000113",*/
];
$websiteUrls = [];

##################################################################################

$bbbApi = new BBBAPIHelper();

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

    $faqList = [];

    if( $sourceCompanyRow["business_started"] )
    {
        $date = strtotime( $sourceCompanyRow["business_started"] );
        if ( $date > mktime( 1, 1, 1, 1, 1, 1500 ) )
        {
            $date = date( "m-d-Y", $date );
            $question = "When {$companyNameWithoutAbbr} was founded?";
            $answer =  "{$companyNameWithoutAbbr} was founded on {$date}.";

            $faqList[] = [
                "question" => $question,
                "answer"   => $answer,
            ];
        }
    }

    if ( $sourceCompanyRow["type_of_entity"] )
    {
        $answer = "{$companyNameWithoutAbbr} is a {$sourceCompanyRow['type_of_entity']}. ";
        $helpers = [
            "Corporation" => "A corporation is a legal entity created by individuals, stockholders, or shareholders, with the purpose of operating for profit. Corporations are allowed to enter into contracts, sue and be sued, own assets, remit federal and state taxes, and borrow money from financial institutions.",
            "Limited Liability Company (LLC)" => "A limited liability company is the US-specific form of a private limited company. It is a business structure that can combine the pass-through taxation of a partnership or sole proprietorship with the limited liability of a corporation.",
            "Cooperative Association" => "A co-operative or co-op is a business that is owned and controlled by its members in order to provide goods or services to those members. Each member pays a membership fee or purchases a membership share and has one vote regardless of the amount of money they have invested in the co-op.",
            "General Partnership" => "A general partnership is a business established by two or more owners. It is the default business structure for multiple owners the same way that a sole proprietorship is the default for solo entrepreneurs.",
            "Limited Liability Partnership (LLP)" => "What is a Limited Liability Partnership (LLP)?\nA limited liability partnership is a partnership in which some or all partners have limited liabilities. It therefore can exhibit elements of partnerships and corporations. In an LLP, each partner is not responsible or liable for another partner's misconduct or negligence.",
            "Limited Partnership" => "A limited partnership is a form of partnership similar to a general partnership except that while a general partnership must have at least two general partners, a limited partnership must have at least one GP and at least one limited partner.",
            "Non-Profit Organization" => "A non-profit organization is a legal entity organized and operated for a collective, public or social benefit, in contrast with an entity that operates as a business aiming to generate a profit for its owners.",
            "Partnership" => "What is a Partnership?\nA partnership is an arrangement where parties, known as business partners, agree to cooperate to advance their mutual interests. The partners in a partnership may be individuals, businesses, interest-based organizations, schools, governments or combinations.",
            "Private Limited Company (LTD)" => "A private limited company is any type of business entity in \"private\" ownership used in many jurisdictions, in contrast to a publicly listed company, with some differences from country to country.",
            "Private Company Limited by Shares" => "What is a Private Company Limited by Shares?\nA private company limited by shares is a class of private limited company incorporated under the laws of England and Wales, Northern Ireland, Scotland, certain Commonwealth countries, and the Republic of Ireland. 
",
            "Professional Corporation" => "Professional corporations or professional service corporation are those corporate entities for which many corporation statutes make special provision, regulating the use of the corporate form by licensed professionals such as attorneys, architects, engineers, public accountants and physicians.",
            "S Corporation" => "An S corp or S corporation is a business structure that is permitted under the tax code to pass its taxable income, credits, deductions, and losses directly to its shareholders. That gives it certain advantages over the more common C corp, The S corp is available only to small businesses with 100 or fewer shareholders, and is an alternative to the limited liability company (LLC).",
            "Sole Proprietorship" => "A sole proprietorship, also known as a sole tradership, individual entrepreneurship or proprietorship, is a type of enterprise owned and run by one person and in which there is no legal distinction between the owner and the business entity. A sole trader does not necessarily work alone and may employ other people.",
        ];

        $advance = "";

        foreach( $helpers as $title => $text )
        {
            if ( strcasecmp( $title, $sourceCompanyRow["type_of_entity"] ) == 0 )
            {
                $advance = $text;
                break;
            }
        }

        if ( !$advance ) die( "Unknown type: ".$sourceCompanyRow["type_of_entity"] );

        $answer .= $advance;

        $faqList[] = [
            "question" => "What type of business entity is {$companyNameWithoutAbbr}?",
            "answer"   => nl2br( $answer ),
        ];
    }

    if ( $sourceCompanyRow['number_of_employees'] )
    {
        $faqList[] = [
            "question" => "How many employees does {$companyNameWithoutAbbr} have?",
            "answer"   => "As per our latest record, {$companyNameWithoutAbbr} has {$sourceCompanyRow['number_of_employees']} employees.",
        ];
    }

    $management = $sourceCompanyRow['business_management'] ?? "";
    $management = trim( $management, " \t\r\n,.-*" );

    if ( $management && 0)
    {
        $faqList[] = [
            "question" => "Who's in charge of {$companyNameWithoutAbbr} business management?",
            "answer"   => "As per our latest record, {$companyNameWithoutAbbr} has {$sourceCompanyRow['number_of_employees']} employees",
        ];
    }

    $area = $sourceCompanyRow['serving_area'] ?? "";
    $area = trim( $area );
    if ( $area )
    {
        $faqList[] = [
            "question" => "What is current serving area of {$companyNameWithoutAbbr}?",
            "answer"   => rtrim( $area, " \t\r\n." ).".",
        ];
    }

    $productAndServices = $sourceCompanyRow["products_and_services"] ?? "";
    $productAndServices = trim( $productAndServices );

    if( $productAndServices )
    {
        $faqList[] = [
            "question" => "What products & services does {$companyNameWithoutAbbr} offer?",
            "answer"   => rtrim( $productAndServices, " \t\r\n." ).".",
        ];
    }

    #####################################################################

    if ( $removeFAQ )
    {
        echo "Remove business FAQ: ".$sourceCompanyRow["company_id"]."\n";

        $savedBusinessID = $exporter->isBusinessExists( $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] ), null );

        if ( $savedBusinessID )
        {
            foreach( $faqList as $faqID => $faqRow )
            {
                if ( !$exporter->removeBusinessFAQByImportID( $exporter->getBusinessFAQImportID( $savedBusinessID, $faqRow["question"] ) ) )
                {
                    die( $exporter->getErrorsAsString() );
                }
            }
        }
    }

    if ( $removeBN )
    {
        echo "Remove business & company: ".$sourceCompanyRow["company_id"]."\n";

        if ( !$exporter->removeCompanyByImportID( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ) ) )
        {
            die( $exporter->getErrorsAsString() );
        }

        if ( !$exporter->removeBusinessByImportID( $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] ) ) )
        {
            die( $exporter->getErrorsAsString() );
        }

        #echo "Remove company: ".$sourceCompanyRow["company_id"]."\n";
    }

    if ( $createAll )
    {
        $destCompanyID = $exporter->addCompany( $exporter->getCompanyImportID( $sourceCompanyRow[ "company_id" ] ), [
            "name"        => $sourceCompanyRow[ "company_name" ]." Scrtd.",
            "import_data" => [
                "company_id"   => $sourceCompanyRow[ "company_id" ],
                "company_name" => $companyNameWithoutAbbr,
                "company_url"  => $sourceCompanyRow[ "url" ],
                "scraper"      => $importInfoScraper,
                "version"      => 1,
            ],
        ] );

        if ( !$destCompanyID )
        {
            die( "Create company error: ".$exporter->getErrorsAsString() );
        }

        echo "New company id: {$destCompanyID}\n";
    }

    $userName = "{$companyNameWithoutAbbr} Support";

    if ( $removeComments )
    {
        echo "Remove user: {$userName}\n";

        if ( !$exporter->removeUserByImportID( $exporter->getUserImportID( $userName ) ) )
        {
            die( $exporter->getErrorsAsString() );
        }
    }

    #####################################################################

    $businessImportID = $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] );

    if ( $createAll )
    {
        $destBusinessID = $exporter->hasBusiness( $destCompanyID );
        if ( !$destBusinessID )
        {
            if ( !preg_match( '#bbb\.org/(us|ca)/#si', $sourceCompanyRow["url"], $match ) )
            {
                echo "Url: ".$sourceCompanyRow["url"]."\n";
                die( "Error:unknown country in url!" );
            }

            $countryShortName = $match[1];

            $hours = $sourceCompanyRow["working_hours"]
                ? HoursFormatter::fromString( $sourceCompanyRow["working_hours"] )
                : null;
            $hours = $hours ? HoursFormatter::convertToCBInternalFormat( $hours ) : null;

            $destBusinessID = $exporter->addBusiness( $businessImportID, [
                "name"        => $companyNameWithoutAbbr,
                "ltd"         => $companyNameOriginal,
                "country"     => $countryShortName,
                "state"       => $sourceCompanyRow["address_region"],
                "city"        => $sourceCompanyRow["address_locality"],
                "address"     => $sourceCompanyRow["street_address"],
                "zip"         => $sourceCompanyRow["postal_code"],
                "hours"       => $hours,
                "phone"       => PhoneFormatter::fromString( $sourceCompanyRow["phone"] ),
                "fax"         => PhoneFormatter::fromString( $sourceCompanyRow["fax_numbers"] ),
                "website"     => WebFormatter::fromString( $sourceCompanyRow[ "website" ] ),
                "category"    => "Other",
                "import_data" => [
                    "company_id"   => $sourceCompanyRow[ "company_id" ],
                    "company_name" => $sourceCompanyRow[ "company_name" ],
                    "company_url"  => $sourceCompanyRow[ "url" ],
                    "scraper"      => $importInfoScraper,
                    "version"      => 1,
                ],
            ] );

            if ( !$destBusinessID )
            {
                die( $exporter->getErrorsAsString() );
            }

            echo "New business id: {$destBusinessID}\n";

            if ( $sourceCompanyRow["logo"] )
            {
                $image = $bbbApi->getLogo( basename( $sourceCompanyRow["logo"] ) );
                if ( $image ) {
                    if ( !$exporter->setBusinessLogo( $businessImportID, $image ) )
                    {
                        die( "setBusinessLogo Error: ".$exporter->getErrorsAsString() );
                    }
                } else {
                    echo "Logo error: ".$bbbApi->getError()."\n";
                }
            }
        } else {
            echo "Use BN id: {$destBusinessID}\n";
        }

        foreach( $faqList as $faqID => $faqRow )
        {
            addBusinessFAQ( $destBusinessID, $exporter, $faqRow["question"], $faqRow["answer"], $sourceCompanyRow );
        }
    }

    if ( !$exporter->linkCompanyToBusiness( $destCompanyID, $destBusinessID ) )
    {
        die( $exporter->getErrorsAsString() );
    }

    # check if business created by scraper or is BN already exists
    $businessRow = $exporter->getBusiness( $businessImportID );
    if ( $businessRow )
    {
        if ( $makeSpamComplaints )
        {
            $exporter->disableBusiness( $businessImportID );
        }
        else
        {
            $exporter->enableBusiness( $businessImportID );
        }
    }

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

            if ( $removeComplaints )
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
            }
        }
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

function addBusinessFAQ( int $businessID, $exporter, string $question, string $answer, array $sourceCompanyRow ): void
{
    global $importInfoScraper;

    $faqImportID = $exporter->getBusinessFAQImportID( $businessID, $question );

    $id = $exporter->addBusinessFAQ( $faqImportID, [
        "business_id" => $businessID,
        "question"    => $question,
        "answer"      => $answer,
        "import_data" => [
            "company_id"   => $sourceCompanyRow[ "company_id" ],
            "company_url"  => $sourceCompanyRow[ "url" ],
            "business_started" => $sourceCompanyRow["business_started"],
            "scraper"      => $importInfoScraper,
            "version"      => 1,
        ]
    ] );

    if ( !$id )
    {
        die( $exporter->getErrorsAsString() );
    }
}