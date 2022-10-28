<?php
namespace DataExport\Exporters;

interface ExportCategoryInterface
{
    public function isCategoryExists( string $categoryName );
}