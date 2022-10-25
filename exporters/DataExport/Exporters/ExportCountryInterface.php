<?php
namespace DataExport\Exporters;

interface ExportCountryInterface
{
    public function isCountryExists( string $name );
    public function isCountryExistsByShortName( string $shortName );
    public function isCountryExistsByFullName( string $fullName );
}