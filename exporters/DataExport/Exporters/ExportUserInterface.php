<?php
namespace DataExport\Exporters;

interface ExportUserInterface
{
    public function getUserImportID( $userId ): string;
    public function removeUserByImportID( string $importID );
    public function isUserExists( string $importID, ?string $userName );
    public function addUser( string $importID, array $fields );
}