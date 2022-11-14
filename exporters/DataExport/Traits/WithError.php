<?php
namespace DataExport\Traits;

trait WithError
{
    private string $error = "";

    public function getError(): string
    {
        return $this->error;
    }

    protected function resetError(): void
    {
        $this->error = "";
    }

    protected function setError( string $error, $return = false )
    {
        $this->error = $error;

        return $return;
    }
}