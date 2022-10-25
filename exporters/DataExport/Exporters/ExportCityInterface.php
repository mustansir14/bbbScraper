<?php
namespace DataExport\Exporters;

interface ExportCityInterface
{
    public function isCityExists( int $countryID, int $stateID, string $name );

    public function getCityImportID( int $countryID, int $stateID, $commentId ): string;
    public function removeCityByImportID( string $importID );
    public function addCity( string $importID, array $fields );
}