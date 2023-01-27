<?php
namespace DataExport\Exporters;

interface ExportCommentInterface
{
    public function getCommentImportID( $commentId, string $type ): string;
    public function removeCommentByImportID( string $importID );
    public function isCommentExists( string $importID );
    public function addComment( string $importID, array $fields );
    public function spamComment( string $importID, string $reason );
    public function unspamComment( string $importID );
}