<?php
namespace DataExport\Exporters;

interface ExportComplaintInterface
{
    public function getComplaintImportID( $complaintId ): string;
    public function removeComplaintByImportID( string $importID );
    public function isComplaintExists( string $importID );
    public function addComplaint( string $importID, array $fields );
}