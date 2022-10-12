<?php
namespace DataExport\Exporters;

interface ExportBusinessInterface
{
    public function getBusinessImportID( $companyId ): string;
    public function removeBusinessByImportID( string $importID );
    public function isBusinessExists( string $importID, ?string $name );
    public function updateBusiness( string $importID, array $fields );
    public function getBusiness( string $importID ): ?array;
    public function addBusiness( string $importID, array $fields );
    public function disableBusiness( string $importID ): bool;
    public function enableBusiness( string $importID ): bool;
}