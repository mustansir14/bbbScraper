<?php
namespace DataExport\Helpers;

class InputChecker
{
    private array $errors;

    public function __construct()
    {
        $this->reset();
    }

    public function reset(): void
    {
        $this->errors = [];
    }

    public function has(): bool
    {
        return count( $this->errors ) > 0;
    }

    public function get(): array
    {
        return $this->errors;
    }

    public function append( string $error ): void
    {
        if ( !$error ) return ;

        $this->errors[] = $error;
    }

    public function empty( $value, string $error ): bool
    {
        if ( empty( $value ) ) {
            $this->append( $error );
            return true;
        }

        return false;
    }
}