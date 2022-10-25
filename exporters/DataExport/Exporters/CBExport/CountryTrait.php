<?php
namespace DataExport\Exporters\CBExport;

trait CountryTrait
{
    public function isCountryExists( string $name )
    {
        $id = $this->isCountryExistsByShortName( $name );
        if ( $id ) return $id;

        $id = $this->isCountryExistsByFullName( $name );
        if ( $id ) return $id;

        return 0;
    }

    public function isCountryExistsByShortName( string $shortName )
    {
        $this->inputChecker->reset();

        $this->inputChecker->empty( $shortName, "Param: 'shortName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        if ( !preg_match( "#^[a-z0-9]{2,3}$#si", $shortName ) )
        {
            return 0;
        }

        $countryID = $this->db->selectColumn( "ID", "countries", [ "country_code" => strtoupper( trim( $shortName ) ) ] );
        $this->throwExceptionIf( $countryID === false, $this->db->getExtendedError() );

        return $countryID ? (int) $countryID: 0;
    }

    public function isCountryExistsByFullName( string $fullName )
    {
        $this->inputChecker->reset();

        $this->inputChecker->empty( $fullName, "Param: 'fullName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        $countryID = $this->db->selectColumn( "ID", "countries", "lower(country_name)='". $this->db->escape( strtolower( trim( $fullName ) ) )."'" );
        $this->throwExceptionIf( $countryID === false, $this->db->getExtendedError() );

        return $countryID ? (int)$countryID: 0;
    }
}