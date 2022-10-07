<?php
namespace DataExport\Exporters;

use DataExport\Exporters\ExportBusinessInterface;
use DataExport\Exporters\ExportCompanyInterface;
use DataExport\Exporters\ExportComplaintInterface;
use DataExport\Exporters\ExportUserInterface;

interface ExportInterface extends ExportBusinessInterface, ExportCompanyInterface, ExportComplaintInterface, ExportUserInterface
{
    public function getErrors(): array;
}