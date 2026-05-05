use strict;
use warnings;
use File::Basename qw(dirname basename);
use File::Copy qw(move);
use JSON::PP;

my $path = shift or die "Usage: perl azure_csv_logs_to_plain.pl <file-path>\n";
my $dir = dirname($path);
my $base = basename($path);
my $target;

if ($base =~ /\.[^.]+\z/) {
    $target = $base;
    $target =~ s/\.[^.]+\z/.log/;
} else {
    $target = $base . '.log';
}

my $target_path = $dir eq '.' ? $target : "$dir/$target";
my $json = JSON::PP->new->canonical->pretty;

open my $in, '<', $path or die "Cannot open $path for reading: $!\n";
my @lines = <$in>;
close $in;

die "File is empty: $path\n" unless @lines;

my $header = shift @lines;
$header =~ s/\r?\n\z//;
$header =~ s/^\xEF\xBB\xBF//;

if ($header ne '"TimeGenerated [UTC]",LogEntry') {
    die "Unexpected header in $path: $header\n";
}

my @out;
for my $line (@lines) {
    $line =~ s/\r?\n\z//;
    next if $line eq '';

    if ($line !~ /^"[^"]*","(.*)"$/) {
        die "Unexpected row format in $path: $line\n";
    }

    my $entry = $1;
    $entry =~ s/""/"/g;

    if ($entry =~ /^(.* - )(\{.*\})$/s) {
        my ($prefix, $payload) = ($1, $2);
        my $decoded = eval { JSON::PP::decode_json($payload) };
        if ($decoded) {
            my $pretty = $json->encode($decoded);
            $pretty =~ s/\n\z//;
            $entry = $prefix . $pretty;
        }
    }

    push @out, $entry;
}

open my $out_fh, '>', $path or die "Cannot open $path for writing: $!\n";
print {$out_fh} join("\n", @out), "\n";
close $out_fh;

if ($target_path ne $path) {
    move($path, $target_path) or die "Cannot rename $path to $target_path: $!\n";
}

print "$target_path\n";