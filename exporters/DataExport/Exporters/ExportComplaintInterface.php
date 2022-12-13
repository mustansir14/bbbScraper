<?php
namespace DataExport\Exporters;

interface ExportComplaintInterface
{
    public function getComplaintImportID( $complaintId, string $type ): string;
    public function removeComplaintByImportID( string $importID );
    public function isComplaintExists( string $importID );
    public function addComplaint( string $importID, array $fields );
    public function spamComplaint( string $importID, string $reason );
    public function unspamComplaint( string $importID );
}