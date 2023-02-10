<?php
namespace DataExport\Exporters;

interface ExportCategoryInterface
{
    public function isCategoryExists(string $parentCategory, ?string $childCategory = null);
    public function getCategoryImportID(string $parentCategory, ?string $childCategory = null): string;
    public function removeCategory(string $parentCategory, ?string $childCategory = null);
    public function addCategory(array $fields);
}