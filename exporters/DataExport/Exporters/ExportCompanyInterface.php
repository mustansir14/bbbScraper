<?php
namespace DataExport\Exporters;

interface ExportCompanyInterface
{
    public function getCompanyImportID( $companyId ): string;
    public function removeCompanyByImportID( string $importID );
    public function isCompanyExists( string $importID, string $name );
    public function addCompany( string $importID, array $fields );
    public function hasBusiness( int $companyID ): int;
    public function linkCompanyToBusiness( int $companyId, int $businessId ): bool;
}