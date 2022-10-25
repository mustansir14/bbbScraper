<?php
namespace DataExport\Exporters;

interface ExportStateInterface
{
    public function isStateExists( int $countryID, string $name );
    public function isStateExistsByShortName( int $countryID, string $shortName );
    public function isStateExistsByFullName( int $countryID, string $fullName );
}