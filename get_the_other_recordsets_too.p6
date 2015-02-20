v6;
use JSON::Tiny;
use HTTP::Client;

my $client = HTTP::Client.new;
  my $response = $client.get('http://api.idigbio.org/v1/recordsets/5ab348ab-439a-4697-925c-d6abe0c09b92');
  if ($response.success) {
     my %rjson = %(from-json($response.content));

     say (%rjson{'idigbio:uuid'});
  }
  else {
    say "An error occured.";
 }
