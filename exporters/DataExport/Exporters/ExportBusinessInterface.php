<?php
namespace DataExport\Exporters;

interface ExportBusinessInterface
{
    public function getBusinessImportID( $companyId ): string;
    public function removeBusinessByImportID( string $importID );
    public function isBusinessExists( string $importID, string $name );
    public function addBusiness( string $importID, array $fields );
}