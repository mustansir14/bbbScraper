<?php
namespace DataExport\Data;

use DataExport\Formatters\PhoneFormatter;
use DataExport\Formatters\WebFormatter;
use DataExport\Formatters\HoursFormatter;
use DataExport\Helpers\BBBAPIHelper;
use DataExport\Helpers\ScreenshotApiHelper;
use DataExport\Data\CompanyData;
use DataExport\Data\FAQData;

class BusinessData
{
    private static function removeFAQ( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr )
    {
        echo "Remove business FAQ: ".$sourceCompanyRow["company_id"]."\n";

        $faqList = FAQData::prepare( $sourceCompanyRow, $companyNameWithoutAbbr );
        if ( $faqList )
        {
            FAQData::removeFAQFromBusiness( $exporter, $sourceCompanyRow[ "company_id" ], $faqList );
        }
    }

    public static function removeAllPosts( object $exporter, array $sourceCompanyRow)
    {
        $businessID = $exporter->isBusinessExists( $exporter->getBusinessImportID( $sourceCompanyRow['company_id'] ), null );
        if ( $businessID )
        {
            foreach ( $exporter->getAllImportedComments( $businessID ) as $comment )
            {
                $exporter->removeCommentByImportID( $comment[ 'import_id' ] );
            }

            foreach ( $exporter->getAllImportedComplaints( $businessID ) as $complaint )
            {
                $exporter->removeComplaintByImportID( $complaint[ 'import_id' ] );
            }
        }
    }

    public static function remove( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr )
    {
        static::removeFAQ( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr );

        $businessID = $exporter->isBusinessExists( $exporter->getBusinessImportID( $sourceCompanyRow['company_id'] ), null );
        if ( $businessID ) {
            echo "Remove business & company: ".$sourceCompanyRow["company_id"]."\n";

            static::removeAllPosts( $exporter, $sourceCompanyRow );

            if ( !$exporter->removeCompanyByImportID( $exporter->getCompanyImportID( $sourceCompanyRow["company_id"] ) ) )
            {
                die( $exporter->getErrorsAsString() );
            }

            if ( !$exporter->removeBusinessByImportID( $exporter->getBusinessImportID( $sourceCompanyRow["company_id"] ) ) )
            {
                die( $exporter->getErrorsAsString() );
            }
        }
    }

    public static function createDbRecord( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr, string $importInfoScraper )
    {
        $businessImportID = $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] );

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
            "ltd"         => $sourceCompanyRow[ "company_name" ],
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

        return $destBusinessID;
    }

    public static function uploadLogo( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr, bool $makeScreenshot )
    {
        $businessImportID = $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] );

        // BN already can exists in db without exportation, do not modify this
        if ( $exporter->isBusinessExported( $businessImportID, $companyNameWithoutAbbr ) )
        {
            echo "Logo: ".$sourceCompanyRow[ "logo" ]."\n";
            echo "Web: ".$sourceCompanyRow[ "website" ]."\n";

            if ( $sourceCompanyRow[ "logo" ] )
            {
                $bbbApi = new BBBAPIHelper();

                $image = $bbbApi->getLogo( basename( $sourceCompanyRow[ "logo" ] ) );
                if ( $image )
                {
                    if ( !$exporter->setBusinessLogo( $businessImportID, $image ) )
                    {
                        die( "setBusinessLogo Error: ".$exporter->getErrorsAsString() );
                    }
                }
                else
                {
                    echo "Logo error: ".$bbbApi->getError()."\n";
                }
            }
            elseif ( $sourceCompanyRow[ "website" ] && filter_var( $sourceCompanyRow[ "website" ], FILTER_VALIDATE_URL ) && $makeScreenshot )
            {
                echo "Making screenshot...\n";
                $screenshot = new ScreenshotApiHelper();
                $reply = $screenshot->getScreenshot( $sourceCompanyRow[ "website" ] );
                if ( !$reply )
                {
                    var_dump( $reply );
                    echo "Error: making screenshot error: ".$screenshot->getError()."\n";
                    exit;
                }
                if ( !$exporter->setBusinessLogo( $businessImportID, $reply->image_content ) )
                {
                    die( "setBusinessLogo Error: ".$exporter->getErrorsAsString() );
                }
            }
        }
    }

    public static function toggleProfile(  object $exporter, array $sourceCompanyRow, bool $makeSpamComplaints )
    {
        $businessImportID = $exporter->getBusinessImportID( $sourceCompanyRow[ "company_id" ] );
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
    }

    private static function addFAQ( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr, string $importInfoScraper, int $destBusinessID)
    {
        $faqList = FAQData::prepare( $sourceCompanyRow, $companyNameWithoutAbbr );
        foreach( $faqList as $faqID => $faqRow )
        {
            $faqImportID = $exporter->getBusinessFAQImportID( $destBusinessID, $faqRow["question"] );

            $id = $exporter->addBusinessFAQ( $faqImportID, [
                "business_id" => $destBusinessID,
                "question"    => $faqRow["question"],
                "answer"      => $faqRow["answer"],
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
    }

    public static function create( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr, string $importInfoScraper, bool $makeScreenshot, bool $makeSpamComplaints )
    {
        $destCompanyID = CompanyData::create( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper );
        if ( !$destCompanyID ) throw new \Exception( "critical" );

        $destBusinessID = $exporter->hasBusiness( $destCompanyID );
        if ( !$destBusinessID )
        {
            $destBusinessID = static::createDbRecord( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper );

            static::toggleProfile(  $exporter, $sourceCompanyRow, $makeSpamComplaints );
            static::uploadLogo( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $makeScreenshot );
        } else {
            echo "Use BN id: {$destBusinessID}\n";
        }

        if ( !$destBusinessID ) throw new \Exception( "critical" );

        static::addFAQ( $exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper, $destBusinessID );

        if ( !$exporter->linkCompanyToBusiness( $destCompanyID, $destBusinessID ) )
        {
            die( $exporter->getErrorsAsString() );
        }

        return [
            $destBusinessID,
            $destCompanyID
        ];
    }
}