<?php
namespace DataExport\Exporters\CBExport;

use DataExport\Formatters\TextFormatter;
use Faker\Provider\Text;

trait CityTrait
{
    public function isCityExists( int $countryID, int $stateID, string $cityName )
    {
        $this->inputChecker->reset();
        $this->inputChecker->notID( $countryID, "Param: 'countryID' not id" );
        $this->inputChecker->notID( $stateID, "Param: 'stateID' not id" );
        $this->inputChecker->empty( $cityName, "Param: 'cityName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        $cityID = $this->db->selectColumn( "ID", "cities",
            "country_id = '{$countryID}' and states_id = '{$stateID}' and lower(city_name)='". $this->db->escape( strtolower( trim( $cityName ) ) )."'" );
        $this->throwExceptionIf( $cityID === false, $this->db->getExtendedError() );

        return $cityID ? (int)$cityID: 0;
    }

    public function getCityImportID( int $countryID, int $stateID, $cityName ): string
    {
        $cityName = strtolower( trim( $cityName ) );
        return "scraper-bbb--country-state-city:{$countryID},{$stateID},{$cityName}";
    }

    public function removeCityByImportID( string $importID )
    {
        $this->inputChecker->reset();
        return $this->removeRecordByImportID( "cities", $importID );
    }

    public function addCity( string $importID, array $fields )
    {
        $this->inputChecker->reset();

        $checker = $this->inputChecker;

        $checker->empty( $importID, "Param: importID is empty" );
        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $countryID = $stateID = 0;

        if ( !$checker->empty( $fields["country"], "Field: 'country' is empty" ) )
        {
            $countryID = $this->isCountryExists( $fields["country"] );
            if ( !$countryID )
            {
                $checker->append( "Country not exists" );
            }
        }

        if ( !$checker->empty( $fields["state"], "Field: 'state' is empty" ) )
        {
            $stateID = $this->isStateExists( $countryID, $fields["state"] );
            if ( !$stateID )
            {
                $checker->append( "State not exists" );
            }
        }

        $ripAddress = TextFormatter::rip( $fields["name"] ?? "" );

        if ( !$checker->empty( $fields['name'], "Field: 'name' is empty" ) )
        {
            if ( !$ripAddress )
            {
                $checker->append( "Rip for name invalid" );
            }
        }
        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $cityID = $this->isCityExists( $countryID, $stateID, $fields["name"] );
        if ( $cityID > 0 ) return $cityID;

        $insertFields = [
            "country_id" => $countryID,
            "states_id"  => $stateID,
            "address"    => $ripAddress,
            "city_name"  => $fields['name'],
        ];

        $rs = $this->db->insert( "cities", $insertFields );
        $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

        $id = $this->db->insertID();

        $this->addImport( "cities", $id, $importID, $fields["import_data"] );

        return $id;
    }
}