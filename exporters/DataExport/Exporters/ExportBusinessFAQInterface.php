<?php
namespace DataExport\Exporters;

interface ExportBusinessFAQInterface
{
    public function getBusinessFAQImportID( int $businessID, string $question ): string;
    public function isBusinessFAQExists( int $businessID, string $importID, ?string $question );
    public function removeBusinessFAQByImportID( string $importID );
    public function addBusinessFAQ( string $importID, array $fields );
}