@echo off

%cd%/vendor/bin/phpunit --colors --stop-on-defect --bootstrap %cd%\tests\bootstrap.php --testdox %1 %2 %3 %4 %5