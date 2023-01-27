<?php

namespace DataExport\Helpers;

use Exception;

class CheckUniqueTextViaCSV
{
    private string    $collectFileName;
    private string    $checkedFileName;
    private string    $mode;
    private $fp;
    private array     $ids;

    public function __construct(string $collectFileName, string $checkedFileName)
    {
        $this->collectFileName = $collectFileName;
        $this->checkedFileName = $checkedFileName;
        $this->mode = 'disabled';
        $this->fp = null;
        $this->ids = [];
    }

    public function setDisabledMode()
    {
        $this->setMode('disabled');
    }

    public function setCollectMode()
    {
        $this->setMode('collect');
    }

    public function setUseMode()
    {
        $this->setMode('use');
    }

    public function isModeCollect(): bool
    {
        return $this->mode === "collect";
    }

    public function isModeUse(): bool
    {
        return $this->mode === "use";
    }

    private function setMode(string $mode)
    {
        if (!in_array($mode, ['disabled', 'collect', 'use'])) {
            throw new Exception("Unknown mode: {$mode}");
        }
        $this->mode = $mode;
        if ($this->mode === 'collect') {
            @unlink($this->collectFileName);
            $this->open($this->collectFileName);
        } elseif ($this->mode === 'use') {
            $this->open($this->checkedFileName);
            while (($data = fgetcsv($this->fp, 1000, ",")) !== false) {
                $this->ids[$data[0]] = $data[2];
            }
            $this->close();
        }
    }

    public function open(string $fileName)
    {
        $fp = fopen($fileName, 'a+');
        if (!$fp) {
            throw new Exception("Can not open {$fileName}");
        }
        $this->fp = $fp;

        return $fp;
    }

    public function close()
    {
        if ($this->fp) {
            fclose($this->fp);
            $this->fp = null;
        }
    }

    public function saveRecord(int $id, string $text)
    {
        if ($this->mode === 'collect') {
            $this->ids[$id] = 1;
            if (!fputcsv($this->fp, [$id, $text])) {
                throw new Exception("Can not save record");
            }
        }
    }

    public function isIDUnique(int $id): bool
    {
        return isset($this->ids[$id]) && $this->ids[$id] === "unique";
    }

}