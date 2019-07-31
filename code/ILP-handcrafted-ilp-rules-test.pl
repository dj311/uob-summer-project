:- multifile(library_directory/1).
library_directory('/metagol').
:- use_module(library(metagol)).

%% metagol settings
body_pred(alloc_mem/1).
body_pred(pointer/1).
body_pred(pointer_written_to/2).
body_pred(alloc_checks_size/1).
body_pred(alloc_doesnt_check_size/1).

%% background knowledge

alloc_mem(bad_location_62852).
alloc_mem(bad_location_62869).
alloc_mem(bad_location_62804).
alloc_mem(good_location_62852).
alloc_mem(good_location_62869).
alloc_mem(good_location_62804).

alloc_checks_size(good_location_62852).
alloc_checks_size(good_location_62869).
alloc_checks_size(good_location_62804).

alloc_doesnt_check_size(MemoryAlloc) :- alloc_mem(MemoryAlloc), not(alloc_checks_size(MemoryAlloc)).

pointer(bad_62804_data).
pointer(bad_62852_data).
pointer(bad_62869_data).
pointer(good_62804_data).
pointer(good_62852_data).
pointer(good_62869_data).

pointer_written_to(bad_62804_data, bad_location_62852).
pointer_written_to(bad_62852_data, bad_location_62869).
pointer_written_to(bad_62869_data, bad_location_62804).
pointer_written_to(good_62804_data, good_location_62852).
pointer_written_to(good_62852_data, good_location_62869).
pointer_written_to(good_62869_data, good_location_62804).

%% metarules
% metarule([P,Q],[P,A,B],[[Q,A,B]]).
% metarule([P,Q,R],[P,A,B],[[Q,A,B],[R,A,B]]).
% metarule([P,Q,R],[P,A,B],[[Q,A,C],[R,C,B]]).

metarule([P,Q,R],[P,A],[[Q,A],[R,A]]).
metarule([P,Q,R],[P,A],[[Q,A,B],[R,B]]).

%% learning task
:-
 %% positive examples
 Pos = [
   bug(bad_62804_data),
   bug(bad_62852_data),
   bug(bad_62869_data)
 ],
 %% negative examples
 Neg = [
   bug(good_62804_data),
   bug(good_62852_data),
   bug(good_62869_data)
 ],
 learn(Pos,Neg).