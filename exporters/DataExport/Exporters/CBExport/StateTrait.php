<?php
namespace DataExport\Exporters\CBExport;

trait StateTrait
{
    public function isStateExists( int $countryID, string $name )
    {
        $id = $this->isStateExistsByShortName( $countryID, $name );
        if ( $id ) return $id;

        $id = $this->isStateExistsByFullName( $countryID, $name );
        if ( $id ) return $id;

        return 0;
    }

    public function isStateExistsByShortName( int $countryID, string $shortName )
    {
        $this->inputChecker->reset();

        $this->inputChecker->notID( $countryID, "Param: 'countryID' is empty" );
        $this->inputChecker->empty( $shortName, "Param: 'shortName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        if ( !preg_match( "#^[a-z0-9]{2,3}$#si", $shortName ) )
        {
            return 0;
        }

        $stateID = $this->db->selectColumn( "id", "states", [
            "countries_id" => $countryID,
            "state_code" => strtoupper( trim( $shortName ) )
        ] );
        $this->throwExceptionIf( $stateID === false, $this->db->getExtendedError() );

        return $stateID ? (int)$stateID : 0;
    }

    public function isStateExistsByFullName( int $countryID, string $fullName )
    {
        $this->inputChecker->reset();

        $this->inputChecker->notID( $countryID, "Param: 'countryID' is empty" );
        $this->inputChecker->empty( $fullName, "Param: 'fullName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        $stateID = $this->db->selectColumn( "id", "states",
            "countries_id = '{$countryID}' AND lower(state_name)='". $this->db->escape( strtolower( trim( $fullName ) ) )."'"
        );

        $this->throwExceptionIf( $stateID === false, $this->db->getExtendedError() );

        return $stateID ? (int)$stateID : 0;
    }
}