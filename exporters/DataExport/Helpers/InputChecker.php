<?php
namespace DataExport\Helpers;

use DataExport\Helpers\Db;

class InputChecker
{
    private array $errors;
    private Db $db;

    public function __construct(Db $db )
    {
        $this->reset();
        $this->db = $db;
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

    public function notBool( $value, string $error ): bool
    {
        if ( !is_bool( $value ) )
        {
            $this->append( $error );
            return true;
        }

        return false;
    }

    public function dbRowNotExists( string $table, string $id, string $error ): bool
    {
        $count = $this->db->countRows( $table, [ "id" => $id ] );
        if ( $count == 0 ) {
            $this->append( $error );
            return true;
        }

        return false;
    }

    public function dbRowExists( string $table, string $id, string $error ): bool
    {
        $count = $this->db->countRows( $table, [ "id" => $id ] );
        if ( $count > 0 ) {
            $this->append( $error );
            return true;
        }

        return false;
    }
}