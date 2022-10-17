<?php
namespace DataExport\Exporters;

interface ExportCommentInterface
{
    public function getCommentImportID( $commentId ): string;
    public function removeCommentByImportID( string $importID );
    public function isCommentExists( string $importID );
    public function addComment( string $importID, array $fields );
}