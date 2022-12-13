<?php
namespace DataExport\Data;

class CompanyData
{
    public static function create( object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr, string $importInfoScraper )
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

        return $destCompanyID;
    }
}