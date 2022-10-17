<?php
namespace DataExport\Exporters;

interface ErrorsAsStringInterface
{
    public function getErrorsAsString(): string;
}